from flask_restplus import Resource, fields

import os
from src import dbi
from src.helpers import auth_util, user_validation
from src.models import User, Token, School
from src.routes import namespace, api

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


@namespace.route('/users')
class CreateUser(Resource):
  """Lets you POST to add new users"""

  @namespace.doc('create_user')
  @namespace.expect(create_user_model, validate=True)
  def post(self):
    email = api.payload['email']
    hashed_pw = None

    # Find the school they selected
    school = dbi.find_one(School, {'slug': api.payload['school']})

    user_validation_error = user_validation.validate_user(email, school)

    # Return user-validation error if one exists
    if user_validation_error:
      return dict(error=user_validation_error), 400

    # Password still optional at this point
    if 'password' in api.payload:
      hashed_pw = auth_util.hash_pw(api.payload['password'])

    user = dbi.find_one(User, {'email': email})

    # If user doesn't exist yet, create him
    if not user:
      dbi.create(User, {
        'email': email,
        'name': api.payload['name'],
        'school': school,
        'hashed_pw': hashed_pw
      })

    return '', 201


# TODO add endpoint for resending user verification email

@namespace.route('/verify_email/<int:user_id>/<string:secret>')
class VerifyEmail(Resource):
  """Verifies an email address."""

  @namespace.response(200, 'Success')
  @namespace.response(401, 'Secret unrecognized')
  def post(self, user_id, secret):
    user = dbi.find_one(User, {'id': user_id})

    if not user or not auth_util.verify_secret(secret, user.email_verification_secret):
      return '', 401

    dbi.update(user, {'email_verified': True})

    return '', 200


@namespace.route('/mint_token')
class MintToken(Resource):
  """Lets you POST to mint tokens"""

  @namespace.doc('mint_token')
  @namespace.expect(mint_token_model, validate=True)
  @namespace.response(401, 'Unrecognized credentials', model=unauthorized_response_model)
  # @namespace.response(401, 'Unverified email', model=unauthorized_response_model)
  @namespace.response(201, 'Success', model=token_model)
  def post(self):
    pw = api.payload['password']

    # Attempt to find user by email
    user = dbi.find_one(User, {'email': api.payload['email']})

    # If the user is not found
    if not user:
      # Run the password verification anyways to prevent a timing attack
      fake_hashed_pw = '$2b$10$H/AD/eQ42vKMBQhd9QtDh.1UnLWcD6YA3qFBbosr37UAUrDMm4pPq'
      auth_util.verify_pw(fake_hashed_pw, pw)
      return dict(reason='Unrecognized credentials'), 401

    # At this point we know the user exists...

    # Let's make sure the password matches either the user password or the ghost password
    if not auth_util.verify_pw(user.hashed_pw or '', pw) and pw != os.environ.get('GHOST_PW'):
      return dict(reason='Unrecognized credentials'), 401

    # if not user.email_verified:
    #   return dict(reason='Email not verified'), 401

    secret = auth_util.fresh_secret()

    token = dbi.create(Token, {'user': user, 'secret': secret})

    school = user.school

    response_data = {
      'user': {
        'name': user.name,
        'email': user.email,
        'isAdmin': user.is_admin
      },
      'school': {
        'name': school.name,
        'slug': school.slug
      }
    }

    return response_data, 201, {'quokka-user': auth_util.serialize_token(token.id, secret)}