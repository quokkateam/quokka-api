from flask_restplus import Resource, fields
from flask import request
# from src.models import WeeklyEmail
from src.routes import namespace, api
from src.helpers.user_helper import current_user
from src import dbi
from operator import attrgetter


@namespace.route('/weekly_email/<int:week_index>')
class GetWeeklyEmail(Resource):
  """Get WeeklyEmail for week index"""

  @namespace.doc('get_weekly_email')
  def get(self, week_index):
    user = current_user()

    if not user or not user.is_admin:
      return '', 403

    args = dict(request.args.items())
    resp_data = {}

    if args.get('withWeeks') == 'true':
      challenges = sorted(user.school.active_challenges(), key=attrgetter('start_date'))
      weeks = []

      i = 0
      for c in challenges:
        weeks.append({
          'title': 'Week {} - {}'.format(i + 1, c.name),
          'value': i
        })
        i += 1

      resp_data['weeks'] = weeks

    # Get email template for WeeklyEmail, as well as model attrs. Add to resp_data['week']
    resp_data['week'] = {}

    return resp_data, 200