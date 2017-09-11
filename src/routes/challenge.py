from flask_restplus import Resource
from src.models import Challenge, User
from src.routes import namespace, api
from src.routes.deco import set_current_user
from src import dbi


@namespace.route('/challenge/<int:week_num>')
class GetChallenge(Resource):
  """Fetch data for a school's challenge page by week number"""

  @namespace.doc('get_challenge')
  @set_current_user
  def get(self, user=None):
    import code; code.interact(local=locals())
    return '', 200