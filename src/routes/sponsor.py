from flask_restplus import Resource, fields
from src.models import Sponsor
from src.routes import namespace, api
from src.helpers.sponsor_helper import format_sponsors
from src.helpers.user_helper import current_user
from src import dbi, logger
from slugify import slugify
from src.integrations.s3 import upload_image
from uuid import uuid4

create_sponsor_model = api.model('Sponsor', {
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

    school = user.school

    sponsor_name = api.payload['name']

    logo_name = '{}-{}'.format(
      slugify(sponsor_name, separator='-', to_lower=True),
      uuid4().get_hex())

    try:
      logo = upload_image(
        data=api.payload['logo'],
        name=logo_name,
        location='sponsors/'
      )
    except BaseException, e:
      logger.error('Error uploading image to S3'.format(e))
      return 'Error uploading provided image', 500

    dbi.create(Sponsor, {
      'school': school,
      'name': sponsor_name,
      'logo': logo,
      'url': api.payload['url']
    })

    sponsors = format_sponsors(school.sponsors)

    return sponsors, 201