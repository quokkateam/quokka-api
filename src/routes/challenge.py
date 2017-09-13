from flask_restplus import Resource
from src.routes import namespace
from src.helpers.user_helper import current_user
from src.helpers.challenge_helper import format_prizes
from operator import attrgetter
from src.challenges import universal_challenge_info
from datetime import datetime


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
    challenges = sorted(school.challenges, key=attrgetter('start_date'))

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
      'prizes': format_prizes(challenge.prizes),
      'suggestions': challenge.suggestions,
      'adjHabits': {
        'prev': prev_habit,
        'next': next_habit
      },
      'links': universal_challenge['links'],
      'extraInfo': universal_challenge['extra_info']
    }

    return resp