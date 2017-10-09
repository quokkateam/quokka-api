from flask_restplus import Resource, fields
from src.routes import namespace, api
from src.helpers.user_helper import current_user
from src.helpers import random_subset
from src.helpers.winner_helper import formatted_winners
from src import dbi
from operator import attrgetter
from datetime import date
from src.models import Winner, User, Prize
from src.mailers import challenge_mailer

choose_winners_model = api.model('Winner', {
  'challenge_id': fields.Integer(required=True)
})


@namespace.route('/winners')
class RestfulWinners(Resource):

  @namespace.doc('get_formatted_winners_list')
  def get(self):
    user = current_user()

    if not user or not user.is_admin:
      return '', 403

    challenges = sorted(user.school.active_challenges(), key=attrgetter('start_date'))

    data = formatted_winners(challenges)

    return data

  @namespace.doc('choose_winners_for_challenge')
  @namespace.expect(choose_winners_model, validate=True)
  def post(self):
    user = current_user()

    if not user or not user.is_admin:
      return '', 403

    school = user.school
    school_challenges = sorted(school.active_challenges(), key=attrgetter('start_date'))
    challenge = [c for c in school_challenges if c.id == api.payload['challenge_id']]

    if challenge:
      challenge = challenge[0]
    else:
      return 'Challenge Not Found', 404

    # if challenge.start_date.date() > date.today():
    #   return '', 401

    prizes = challenge.prizes

    # Make sure winners haven't already been chosen
    challenge_winners = dbi.find_all(Winner, {
      'prize_id': [p.id for p in prizes]
    })

    if challenge_winners:
      return 'Winners already chosen for this challenge', 500

    all_challenge_prizes = dbi.find_all(Prize, {
      'challenge_id': [c.id for c in school_challenges]
    })

    past_winners = []
    for p in all_challenge_prizes:
      past_winners += p.winners

    past_winner_users = dbi.find_all(User, {'id': [w.user_id for w in past_winners]})

    potential_winner_user_ids = [u.id for u in school.users if u.id not in past_winner_users]

    if not potential_winner_user_ids:
      return 'Everyone has already won!', 501

    potential_winners = dbi.find_all(User, {'id': potential_winner_user_ids})

    prize_ids_for_winners = []
    for p in prizes:
      prize_ids_for_winners += ([p.id] * p.count)

    winning_users = random_subset(potential_winners, len(prize_ids_for_winners))

    i = 0
    for u in winning_users:
      prize_id = prize_ids_for_winners[i]

      # Create the winner
      winner = dbi.create(Winner, {
        'user': u,
        'prize_id': prize_id
      })

      # Send the winner an email congratulating him/her
      challenge_mailer.congratulate_winner(challenge, winner.prize, u, school)

      i += 1

    data = formatted_winners(school_challenges)

    return data