from flask_restplus import Resource
from src.routes import namespace, api
from src.integrations import slack


@namespace.route('/inquire')
class RegisterInquiry(Resource):
  """Inquire about joining the Quokka Challenge as a school"""

  @namespace.doc('register_inquiry')
  def post(self):
    email = api.payload.get('email')
    school = api.payload.get('school')

    if not email or not school:
      return 'Both email and school required for inquiry', 400

    slack.log_inquiry(school, email)
    return '', 200