from flask_restplus import Resource, fields
from src.routes import namespace, api
from src.helpers.user_helper import current_user
from src.helpers import random_subset
from src.helpers.winner_helper import formatted_winners
from src import dbi
from operator import attrgetter
from datetime import date
from src.models import Winner, User, Prize, CheckInAnswer
from src.mailers import challenge_mailer
from random import shuffle

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
    # NOTE: Very aware this endpoint makes a shit-ton of queries and most everything should
    # be eager loaded, but I don't have time to figure all that syntax bullshit out right now for
    # properly eager loading. TODO: Refactor this
    user = current_user()

    if not user or not user.is_admin:
      return '', 403

    school = user.school
    challenges = sorted(school.active_challenges(), key=attrgetter('start_date'))

    # Get challenge to assign winners for
    challenge = [c for c in challenges if c.id == api.payload['challenge_id']]

    # Make sure challenge exists...
    if challenge:
      challenge = challenge[0]
    else:
      return 'Challenge Not Found', 404

    # If challenge hasn't started yet, error out
    if challenge.start_date.date() > date.today():
      return '', 401

    # Get prizes for this challenge
    prizes = sorted(challenge.prizes, key=attrgetter('id'))
    prize_ids = [p.id for p in prizes]

    # Error out if winners have already been chosen for this challenge
    if dbi.find_all(Winner, {'prize_id': prize_ids}):
      return 'Winners already chosen for this challenge', 500

    # Get reference to all prizes across all challenges for this school
    school_prizes = dbi.find_all(Prize, {
      'challenge_id': [c.id for c in challenges]
    })

    # Get list of all past winners for this school
    past_winners = []
    for p in school_prizes:
      past_winners += p.winners

    # Find user_ids for all past winners
    past_winner_user_ids = [u.id for u in dbi.find_all(User, {'id': [w.user_id for w in past_winners]})]

    # Get all check_in_question_ids for this check_in and sort them
    question_ids = [q.id for q in challenge.check_in.check_in_questions]
    question_ids.sort()

    # Find ALL check_in_answers related to these check_in_questions
    answers = dbi.find_all(CheckInAnswer, {'check_in_question_id': question_ids})

    # Create a map of user_id to list of check_in_question_ids that they answered for this check_in
    # Ex: {1: [2, 3, 4]} --> we'll then compare [2, 3, 4] to question_ids to see if they match
    user_ids_to_question_ids = {}
    for a in answers:
      if a.user_id not in user_ids_to_question_ids:
        user_ids_to_question_ids[a.user_id] = [a.check_in_question_id]
      else:
        user_ids_to_question_ids[a.user_id].append(a.check_in_question_id)

    # Find users who:
    # (1) haven't been selected as winners in the past
    # (2) have answered all check_in_questions for this check_in
    potential_winner_user_ids = []
    for k, v in user_ids_to_question_ids.items():
      v.sort()
      if k not in past_winner_user_ids and v == question_ids:
        potential_winner_user_ids.append(k)

    if not potential_winner_user_ids:
      return 'No users currently eligible for prizes -- either everyone has already won or no one has filled out check-ins', 400

    potential_winning_users = dbi.find_all(User, {'id': potential_winner_user_ids})

    prize_ids_for_winners = []
    for p in prizes:
      prize_ids_for_winners += ([p.id] * p.count)

    # Random prize assignment
    shuffle(prize_ids_for_winners)

    winning_users = random_subset(potential_winning_users, len(prize_ids_for_winners))

    i = 0
    for u in winning_users:
      winner = dbi.create(Winner, {
        'user': u,
        'prize_id': prize_ids_for_winners[i]
      })

      # Send the winner an email congratulating him/her
      challenge_mailer.congratulate_winner(challenge, winner.prize, u, school)

      i += 1

    data = formatted_winners(challenges)

    return data