from flask_restplus import Resource, fields
from src.routes import namespace, api
from src.helpers.user_helper import current_user
from src.helpers import random_subset
from src.helpers.winner_helper import formatted_winners
from src import dbi
from operator import attrgetter
from datetime import date
from src.models import Winner, User
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

    if challenge.winners:
      return 'Winners have already been selected for this challenge', 500

    if challenge.start_date.date() > date.today():
      return '', 401

    past_winners = [w.user_id for w in dbi.find_all(Winner, {
      'challenge_id': [c.id for c in school_challenges]
    })]

    # Question: Can admins win prizes too, or should we filter them out?

    potential_winner_user_ids = [u.id for u in school.users if u.id not in past_winners]

    if len(potential_winner_user_ids) == 0:
      return 'Everyone has already won!', 501

    potential_winners = dbi.find_all(User, {'id': potential_winner_user_ids})

    num_winners = len(challenge.prizes)

    winners = random_subset(potential_winners, num_winners)

    for winner in winners:
      # Create the winner
      dbi.create(Winner, {
        'challenge': challenge,
        'user': winner
      })

      # Send the winner an email congratulating him/her
      challenge_mailer.congratulate_winner(challenge, winner)

    data = formatted_winners(school_challenges)

    return data