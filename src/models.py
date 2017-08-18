from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

import auth_util

db = SQLAlchemy()
migrate = Migrate()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    hashed_pw = db.Column(db.String(120))
    email_verified = db.Column(db.Boolean(), default=False)
    email_verification_secret = db.Column(db.String(64))

    def __init__(self, email, hashed_pw):
        self.email = email
        self.hashed_pw = hashed_pw
        self.email_verification_secret = auth_util.fresh_secret()

    def __repr__(self):
        return '<User %r>' % self.email

class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    secret = db.Column(db.String(64))
    user = db.relationship('User', backref='tokens')

    def __init__(self, user, secret):
        self.user = user
        self.secret = secret

    def __repr__(self):
        return '<Token %r>' % self.id
