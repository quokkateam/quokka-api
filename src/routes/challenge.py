from flask_restplus import Resource, fields
from src.routes import namespace, api
from src.helpers.user_helper import current_user
from src.helpers.prize_helper import format_prizes
from src.helpers.sponsor_helper import format_sponsors
from src.helpers.challenge_helper import format_challenges, current_week_num
from operator import attrgetter
from src.challenges import universal_challenge_info
from datetime import datetime, timedelta
from src import dbi, logger
from src.models import Challenge
from src.helpers.error_codes import CHALLENGE_NOT_EXIST, INVALID_CHALLENGE_ACCESS


update_challenge_section_model = api.model('Challenge', {
  'id': fields.Integer(required=True),
  'text': fields.String(required=True),
  'points': fields.Integer(required=True)
})

# TODO: Validate JSON field types for 'suggestions' and 'challenges' below
# update_suggestions_model = api.model('Challenge', {
#   'id': fields.Integer(required=True),
#   'suggestions': fields.String(required=True)
# })

# update_challenges_model = api.model('Challenge', {
#   'challenges': fields.String(required=True),
#   'startDate': fields.String(required=True)
# })


@namespace.route('/challenge/<int:week_num>')
class GetChallenge(Resource):
  """Fetch data for a school's challenge page by week number"""

  @namespace.doc('get_challenge')
  def get(self, week_num):
    user = current_user()

    if not user:
      return '', 403

    school = user.school
    week_index = week_num - 1

    # Get challenges for school, sorted by date
    challenges = sorted(school.active_challenges(), key=attrgetter('start_date'))

    if week_num < 1 or week_num > len(challenges):
      return {'error': 'Challenge does not exist', 'code': CHALLENGE_NOT_EXIST}, 400

    curr_week_num = current_week_num(challenges)

    # if this is a future week and the user isn't an admin, prevent access
    if week_num > curr_week_num and not user.is_admin:
      return {'error': 'Week not yet available to access', 'code': INVALID_CHALLENGE_ACCESS}, 400

    # Find the challenge requested by week index
    challenge = challenges[week_index]

    if week_index == 0:
      prev_habit = None
      next_habit = {
        'weekNum': 2,
        'name': challenges[1].name
      }
    elif week_index == len(challenges) - 1:
      prev_habit = {
        'weekNum': week_index,
        'name': challenges[week_index - 1].name
      }
      next_habit = None
    else:
      prev_habit = {
        'weekNum': week_index,
        'name': challenges[week_index - 1].name
      }
      next_habit = {
        'weekNum': week_num + 1,
        'name': challenges[week_num].name
      }

    # if this is the current week and the user isn't an admin, he/she shouldn't have a link to the next week yet
    if week_num == curr_week_num and not user.is_admin:
      next_habit = None

    universal_challenge = universal_challenge_info.get(challenge.slug)

    resp = {
      'id': challenge.id,
      'habit': {
        'name': challenge.name,
        'slug': challenge.slug,
        'icon': universal_challenge['icon'],
        'dates': {
          'start': datetime.strftime(challenge.start_date, '%m/%d/%Y'),
          'end': datetime.strftime(challenge.end_date, '%m/%d/%Y')
        }
      },
      'overview': universal_challenge['overview'],
      'challenge': {
        'text': challenge.text,
        'points': challenge.points
      },
      'prizes': format_prizes(challenge.active_prizes()),
      'sponsors': format_sponsors(school.sponsors),
      'suggestions': challenge.suggestions,
      'adjHabits': {
        'prev': prev_habit,
        'next': next_habit
      },
      'links': universal_challenge['links'],
      'extraInfo': universal_challenge['extra_info']
    }

    return resp


@namespace.route('/challenge/challenge')
class UpdateChallengeSection(Resource):
  """Save the text and points for a weekly challenge"""

  @namespace.doc('update_challenge_section')
  @namespace.expect(update_challenge_section_model, validate=True)
  def put(self):
    user = current_user()

    if not user or not user.is_admin:
      return '', 403

    challenge = dbi.find_one(Challenge, {'id': api.payload['id']})

    if not challenge:
      logger.error('No challenge found for id: {}'.format(api.payload['id']))
      return 'Challenge required to update text and points', 500

    dbi.update(challenge, {
      'text': api.payload['text'],
      'points': api.payload['points'] or 0
    })

    return {'text': challenge.text, 'points': challenge.points}


@namespace.route('/challenge/suggestions')
class UpdateSuggestions(Resource):
  """Save the suggestions for a weekly challenge"""

  @namespace.doc('update_suggestions')
  # @namespace.expect(update_suggestions_model, validate=True)
  def put(self):
    user = current_user()

    if not user or not user.is_admin:
      return '', 403

    challenge = dbi.find_one(Challenge, {'id': api.payload['id']})

    if not challenge:
      logger.error('No challenge found for id: {}'.format(api.payload['id']))
      return 'Challenge required to update text and points', 500

    dbi.update(challenge, {'suggestions': api.payload['suggestions']})

    return {'suggestions': challenge.suggestions}


@namespace.route('/challenges')
class RestfulChallenges(Resource):
  """Fetch all challenges for a school"""

  @namespace.doc('get_challenges')
  def get(self):
    user = current_user()

    if not user:
      return '', 403

    # Get challenges for school, sorted by date
    challenges = sorted(user.school.active_challenges(), key=attrgetter('start_date'))

    curr_week_num = current_week_num(challenges)

    challenges_data = format_challenges(challenges, user, curr_week_num=curr_week_num)

    resp = {
      'weekNum': curr_week_num,
      'challenges': challenges_data
    }

    return resp

  @namespace.doc('update_challenges')
  # @namespace.expect(update_challenges_model, validate=True)
  def put(self):
    user = current_user()

    if not user or not user.is_admin:
      return '', 403

    try:
      start_date = datetime.strptime(api.payload['startDate'], '%m/%d/%y')
    except:
      return 'Invalid start date', 500

    challenge_slugs = [c['slug'] for c in api.payload['challenges']]

    school = user.school

    challenges = dbi.find_all(Challenge, {
      'school': user.school,
      'slug': challenge_slugs
    })

    i = 0
    for slug in challenge_slugs:
      challenge = [c for c in challenges if c.slug == slug][0]

      if i > 0:
        start_date = start_date + timedelta(days=7)

      end_date = start_date + timedelta(days=6)

      dbi.update(challenge, {'start_date': start_date, 'end_date': end_date})

      i += 1

    challenges = sorted(school.active_challenges(), key=attrgetter('start_date'))

    curr_week_num = current_week_num(challenges)

    challenges_data = format_challenges(challenges, user, curr_week_num=curr_week_num)

    resp = {
      'weekNum': curr_week_num,
      'challenges': challenges_data
    }

    return resp