from flask_restplus import Resource, fields
from src.models import Sponsor, School
from src.routes import namespace, api
from src.helpers.sponsor_helper import format_sponsors
from src.helpers.user_helper import current_user
from src import dbi

create_sponsor_model = api.model('Sponsor', {
  'schoolSlug': fields.String(required=True),
  'logo': fields.String(required=True),
  'name': fields.String(required=True),
  'url': fields.String(required=True)
})


@namespace.route('/sponsor')
class RestfulSponsor(Resource):

  @namespace.doc('create_sponsor')
  @namespace.expect(create_sponsor_model, validate=True)
  def post(self):
    user = current_user()

    if not user or not user.is_admin:
      return '', 403

    school = dbi.find_one(School, {'slug': api.payload['schoolSlug']})

    if not school:
      return 'School required to create sponsor', 500

    dbi.create(Sponsor, {
      'school': school,
      'name': api.payload['name'],
      'logo': api.payload['logo'],
      'url': api.payload['url']
    })

    sponsors = format_sponsors(school.sponsors)

    return sponsors, 201