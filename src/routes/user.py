from flask_restplus import Resource, fields
from src import auth_util
from src import email_client
from src.models import Token, User
from src.routes import api, namespace
import src.dbi as dbi

user_model = api.model('User', {
  'id': fields.Integer(readOnly=True, description='The user unique identifier'),
  'email': fields.String(),
})

create_user_model = api.model('User', {
  'email': fields.String(),
  'password': fields.String(),
})

mint_token_model = api.model('Credentials', {
  'email': fields.String(),
  'password': fields.String(),
})

unauthorized_response_model = api.model('Unauthorized', {
  'reason': fields.String(),
})

token_model = api.model('Token', {
  'token': fields.String(),
})


@namespace.route('/users')
class CreateUser(Resource):
  """Lets you POST to add new users"""

  @namespace.doc('create_user')
  @namespace.expect(create_user_model)
  @namespace.marshal_with(user_model, code=201)
  def post(self):
    user = dbi.create(User, {
      'hased_pw': auth_util.hash_pw(api.payload['password']),
      'email': api.payload['email']
    })

    email_client.send_verification_email(user)

    return user, 201


# TODO add endpoint for resending user verification email

@namespace.route('/verify_email/<int:user_id>/<string:secret>')
class VerifyEmail(Resource):
  """Verifies an email address."""

  @namespace.response(200, 'Success')
  @namespace.response(401, 'Secret unrecognized')
  def post(self, user_id, secret):
    sess = dbi.create_session()
    user = dbi.find_one(User, {'id': user_id}, session=sess)

    if user and auth_util.verify_secret(secret, user.email_verification_secret):
      dbi.update(user, {'email_verified': True}, session=sess)
      return '', 200

    return '', 401


@namespace.route('/mint_token')
class MintToken(Resource):
  """Lets you POST to mint tokens"""

  @namespace.doc('mint_token')
  @namespace.expect(mint_token_model)
  @namespace.response(401, 'Unrecognized credentials', model=unauthorized_response_model)
  @namespace.response(401, 'Unverified email', model=unauthorized_response_model)
  @namespace.response(201, 'Success', model=token_model)
  def post(self):
    sess = dbi.create_session()
    user = dbi.find_one(User, {'email': api.payload['email']}, session=sess)

    if not auth_util.verify_pw(user.hashed_pw or '', api.payload['password']):
      return dict(reason='Unrecognized credentials'), 401

    if not user.email_verified:
      return dict(reason='Email not verified'), 401

    secret = auth_util.fresh_secret()
    token = dbi.create(Token, {'user_id': user.id, 'secret': secret}, session=sess)

    return dict(token=auth_util.serialize_token(token.id, secret)), 201
