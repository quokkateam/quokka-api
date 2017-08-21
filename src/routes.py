from flask_restplus import Api, Resource, fields

import auth_util
import email_client
from integrations import slack
import user_validation
from models import db, Token, User, School

api = Api(version='0.1', title='Quokka API')
namespace = api.namespace('api')

create_user_model = api.model('User', {
  'email': fields.String(required=True),
  'name': fields.String(required=True),
  'school': fields.String(required=True),
  'password': fields.String(required=False),
})

mint_token_model = api.model('Credentials', {
  'email': fields.String(required=True),
  'password': fields.String(required=True),
})

unauthorized_response_model = api.model('Unauthorized', {
  'reason': fields.String(),
})

token_model = api.model('Token', {
  'token': fields.String(),
})

school_model = api.model('School', {
  'name': fields.String(),
  'slug': fields.String(),
  'domains': fields.List(fields.String()),
})

schools_model = api.model('Schools', {
  'schools': fields.List(fields.Nested(school_model)),
})

letsencrypt = api.namespace('.well-known')
@letsencrypt.route('/acme-challenge/KjAkaz_AWW5MheB8uYkrB9n-bYGcj0GIm-5WrjCAmck')
class LetsEncrypt(Resource):
  def get(self):
    return 'KjAkaz_AWW5MheB8uYkrB9n-bYGcj0GIm-5WrjCAmck.EhpvvnfVgLYBmolxucvxugRb9BB9AKa5TTEZzlG8z6U', 200


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


@namespace.route('/schools')
class GetSchools(Resource):
  """Fetch all non-destroyed Schools"""

  @namespace.doc('get_schools')
  @namespace.marshal_with(schools_model)
  def get(self):
    schools = School.query.all()
    school_data = [{'name': s.name, 'slug': s.slug, 'domains': s.domains} for s in schools]
    return {'schools': school_data}


@namespace.route('/users')
class CreateUser(Resource):
  """Lets you POST to add new users"""

  @namespace.doc('create_user')
  @namespace.expect(create_user_model, validate=True)
  def post(self):
    user_exists_already = User.query.filter_by(email=api.payload['email']).first() is not None
    school = School.query.filter_by(slug=api.payload['school']).first()
    user_validation_error = user_validation.validate_user(api.payload['email'], school)
    if user_validation_error is not None:
      return dict(error=user_validation_error), 400
    if 'password' in api.payload:
      hashed_pw = auth_util.hash_pw(api.payload['password'])
    else:
      hashed_pw = None
    if user_exists_already:
      # TODO notify user
      pass
    else:
      user = User(
        hashed_pw=hashed_pw,
        email=api.payload['email'],
        name=api.payload['name'],
        school=school)
      db.session.add(user)
      db.session.commit()
      email_client.send_verification_email(user)
    return '', 201


# TODO add endpoint for resending user verification email

@namespace.route('/verify_email/<int:user_id>/<string:secret>')
class VerifyEmail(Resource):
  """Verifies an email address."""

  @namespace.response(200, 'Success')
  @namespace.response(401, 'Secret unrecognized')
  def post(self, user_id, secret):
    user = User.query.filter_by(id=user_id).first()
    if user is not None and auth_util.verify_secret(
      secret, user.email_verification_secret):
      user.email_verified = True
      db.session.add(user)
      db.session.commit()
      return '', 200
    return '', 401


@namespace.route('/mint_token')
class MintToken(Resource):
  """Lets you POST to mint tokens"""

  @namespace.doc('mint_token')
  @namespace.expect(mint_token_model, validate=True)
  @namespace.response(401, 'Unrecognized credentials', model=unauthorized_response_model)
  @namespace.response(401, 'Unverified email', model=unauthorized_response_model)
  @namespace.response(201, 'Success', model=token_model)
  def post(self):
    user = User.query.filter_by(email=api.payload['email']).first()
    if user is not None and user.hashed_pw is not None:
      hashed_pw = user.hashed_pw
      can_mint_token = True
    else:
      # Turns out auth_util.verify_pw returns immediately if hashed_pw =
      # '', so use a dummy hash. Doesn't matter what it's of because of
      # can_mint_token flag.
      hashed_pw = '$2b$10$H/AD/eQ42vKMBQhd9QtDh.1UnLWcD6YA3qFBbosr37UAUrDMm4pPq'
      can_mint_token = False
    if auth_util.verify_pw(hashed_pw, api.payload['password']) and can_mint_token:
      if not user.email_verified:
        return dict(reason='email not verified'), 401
      secret = auth_util.fresh_secret()
      token = Token(user, secret)
      db.session.add(token)
      db.session.commit()
      return dict(token=auth_util.serialize_token(token.id, secret)), 201
    else:
      return dict(reason='Unrecognized credentials'), 401
