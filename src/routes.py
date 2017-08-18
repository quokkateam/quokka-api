from flask_restplus import Api, Resource, fields

import auth_util
import email_client
from models import db, Token, User

api = Api(version='0.1', title='Quokka API')
namespace = api.namespace('api')

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

@namespace.route('/users/')
class AddUser(Resource):
    """Lets you POST to add new users"""

    @namespace.doc('create_user')
    @namespace.expect(create_user_model)
    @namespace.marshal_with(user_model, code=201)
    def post(self):
        # TODO do something graceful on unique email integrity constraint violation.
        from flask import request
        user = User(
            hashed_pw=auth_util.hash_pw(api.payload['password']),
            email=api.payload['email'])
        db.session.add(user)
        db.session.commit()
        email_client.send_verification_email(user)
        return user, 201

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
    @namespace.expect(mint_token_model)
    @namespace.response(401, 'Unrecognized credentials', model=unauthorized_response_model)
    @namespace.response(401, 'Unverified email', model=unauthorized_response_model)
    @namespace.response(201, 'Success', model=token_model)
    def post(self):
        user = User.query.filter_by(email=api.payload['email']).first()
        if user is not None:
            hashed_pw = user.hashed_pw
        else:
            hashed_pw = ''
        if auth_util.verify_pw(hashed_pw, api.payload['password']):
            if not user.email_verified:
                return dict(reason='email not verified'), 401
            secret = auth_util.fresh_secret()
            token = Token(user, secret)
            db.session.add(token)
            db.session.commit()
            return dict(token=auth_util.serialize_token(token.id, secret)), 201
        else:
            return dict(reason='Unrecognized credentials'), 401
