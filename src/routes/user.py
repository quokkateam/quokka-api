from flask_restplus import Resource, fields
import os
from operator import attrgetter
from datetime import date
from src import dbi, logger
from src.helpers import auth_util, user_validation, decode_url_encoded_str
from src.helpers.user_helper import current_user
from src.models import User, Token, School
from src.routes import namespace, api
from src.mailers import user_mailer

create_user_model = api.model('User', {
  'email': fields.String(required=True),
  'name': fields.String(required=True),
  'age': fields.String(required=False),
  'gender': fields.String(required=False),
  'school': fields.String(required=True)
})

verify_email_model = api.model('VerifyEmail', {
  'userId': fields.Integer(required=True),
  'token': fields.String(required=True)
})

verify_demo_token_model = api.model('VerifyDemoToken', {
  'token': fields.String(required=True)
})

trigger_forgot_pw_email_model = api.model('TriggerForgotPwEmail', {
  'email': fields.String(required=True)
})

forgot_pw_model = api.model('ForgotPassword', {
  'userId': fields.Integer(required=True),
  'token': fields.String(required=True)
})

update_pw_model = api.model('UpdatePassword', {
  'password': fields.String(required=True),
  'dorm': fields.String(required=False)
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

invite_user_model = api.model('InviteUserModel', {
  'email': fields.String(required=True)
})


@namespace.route('/users')
class CreateUser(Resource):
  """Lets you POST to add new users"""

  @namespace.doc('create_user')
  @namespace.expect(create_user_model, validate=True)
  def post(self):
    logger.info("Receiving this request!!!!!")
    logger.error("Receiving this request!!!!!")
    print "Receiving this request!!!"

    return {'launched': launched}, 201

    email = api.payload['email'].lower()

    # Find the school they selected
    school = dbi.find_one(School, {'slug': api.payload['school']})

    # user_validation_error = user_validation.validate_user(email, school)

    # # Return user-validation error if one exists
    # if user_validation_error:
    #   return dict(error=user_validation_error), 400

    user = dbi.find_one(User, {'email': email})

    challenges = sorted(school.active_challenges(), key=attrgetter('start_date'))
    launched = len(challenges) > 0 and date.today() >= challenges[0].start_date.date() and school.launchable

    # If user doesn't exist yet, create him
    if not user:
      logger.info('Adding {} to database...'.format(api.payload['gender']))
      user = dbi.create(User, {
        'email': email,
        'name': api.payload['name'],
        'age': api.payload['age'],
        'gender': api.payload['gender'],
        'school': school
      })

      if launched:
        email_sent = user_mailer.complete_account(user)

        if email_sent:
          dbi.update(user, {'email_verification_sent': True})

    return {'launched': launched}, 201


@namespace.route('/verify_email')
class VerifyEmail(Resource):
  """Verifies an email address."""

  @namespace.doc('verify_email')
  @namespace.expect(verify_email_model, validate=True)
  def post(self):
    user = dbi.find_one(User, {'id': api.payload['userId']})

    provided_token = decode_url_encoded_str(api.payload['token'])

    if not user or not auth_util.verify_secret(provided_token, user.email_verification_secret):
      return '', 401

    user = dbi.update(user, {'email_verified': True})

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

    return response_data, 200, {'quokka-user': auth_util.serialize_token(token.id, secret)}


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
    email = api.payload['email'].lower()

    # Attempt to find user by email
    user = dbi.find_one(User, {'email': email})

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


@namespace.route('/update_password')
class UpdatePassword(Resource):
  """User updating his/her password."""

  @namespace.doc('update_password')
  @namespace.expect(update_pw_model, validate=True)
  def put(self):
    user = current_user()

    if not user:
      return '', 403

    updates = {
      'hashed_pw': auth_util.hash_pw(api.payload['password'])
    }

    if user.school.slug == 'rice-university' and api.payload.get('dorm'):
      updates['meta'] = {'dorm': api.payload['dorm']}

    dbi.update(user, updates)

    return '', 200


@namespace.route('/verify_demo_token')
class VerifyDemoToken(Resource):
  """Ensure demo token is valid."""

  @namespace.doc('verify_demo_token')
  @namespace.expect(verify_demo_token_model, validate=True)
  def post(self):
    demo_token = os.environ.get('DEMO_TOKEN')
    submitted_token = decode_url_encoded_str(api.payload['token'])

    if not auth_util.verify_pw(submitted_token, demo_token):
      return '', 403

    user = dbi.find_one(User, {'email': 'demouser@demo.edu'})

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

    return response_data, 200, {'quokka-user': auth_util.serialize_token(token.id, secret)}


@namespace.route('/trigger_forgot_pw_email')
class TriggerForgotPwEmail(Resource):
  """Send reset password email to user."""

  @namespace.doc('trigger_forgot_pw_email')
  @namespace.expect(trigger_forgot_pw_email_model, validate=True)
  def post(self):
    email = api.payload['email']
    user = dbi.find_one(User, {'email': email})

    if not user:
      return '', 400

    # Give user a reset password token
    user = dbi.update(user, {'reset_pw_secret': auth_util.fresh_secret()})

    # Send user an email with a link to reset pw
    user_mailer.reset_password(user)

    return '', 200


@namespace.route('/forgot_password')
class ForgotPassword(Resource):
  """Validate a user's reset_pw_secret"""

  @namespace.doc('forgot_password')
  @namespace.expect(forgot_pw_model, validate=True)
  def post(self):
    user = dbi.find_one(User, {'id': api.payload['userId']})

    if not user or not user.reset_pw_secret:
      return '', 401

    provided_token = decode_url_encoded_str(api.payload['token'])

    if not auth_util.verify_secret(provided_token, user.reset_pw_secret):
      return '', 401

    user = dbi.update(user, {'reset_pw_secret': None})

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

    return response_data, 200, {'quokka-user': auth_util.serialize_token(token.id, secret)}


@namespace.route('/users/invite')
class InviteUser(Resource):
  """Invite a user on behalf of another user"""

  @namespace.doc('invite_user')
  @namespace.expect(invite_user_model, validate=True)
  def post(self):
    from_user = current_user()

    if not from_user:
      return '', 403

    to_email = api.payload['email']
    to_user = dbi.find_one(User, {'email': to_email})

    if to_user:
      return 'User already on Quokka', 500

    user_mailer.invite_user(from_user, to_email)

    return '', 200