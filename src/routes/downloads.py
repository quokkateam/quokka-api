from flask_restplus import Resource
from src.helpers.user_helper import current_user, format_school_users_csv
from src.routes import namespace


@namespace.route('/downloads/all_school_users')
class GetAllUsersForSchool(Resource):
  """Get all users for a school"""

  @namespace.doc('all_school_users')
  def get(self):
    user = current_user()

    if not user or not user.is_admin:
      return '', 403

    csv_data = format_school_users_csv(user.school)

    resp = {
      'content': csv_data,
      'filename': 'all-users.csv'
    }

    return resp