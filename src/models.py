from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.dialects.postgresql import JSON
from slugify import slugify

import auth_util
import datetime

db = SQLAlchemy()
migrate = Migrate()

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String(120), index=True, unique=True)
  hashed_pw = db.Column(db.String(120))
  email_verified = db.Column(db.Boolean(), default=False)
  email_verification_secret = db.Column(db.String(64))
  school_id = db.Column(db.Integer, db.ForeignKey('school.id'), index=True, nullable=False)
  # TODO make a helper for querying all live users
  is_destroyed = db.Column(db.Boolean(), default=False)
  created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
  school = db.relationship('School', backref='users')

  def __init__(self, email, hashed_pw):
    self.email = email
    self.hashed_pw = hashed_pw
    self.email_verification_secret = auth_util.fresh_secret()

  def __repr__(self):
    return '<User %r, id=%d>' % (self.email, self.id)


class Token(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True, nullable=False)
  secret = db.Column(db.String(64))
  user = db.relationship('User', backref='tokens')

  def __init__(self, user, secret):
    self.user = user
    self.secret = secret

  def __repr__(self):
    return '<Token %r>' % self.id


class School(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(120), unique=True)
  slug = db.Column(db.String(120), index=True)
  domains = db.Column(JSON, default=[])
  is_destroyed = db.Column(db.Boolean(), default=False)
  created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

  def __init__(self, name, domains):
    self.name = name
    self.slug = slugify(name, separator='-', to_lower=True)
    self.domains = domains
    self.email_verification_secret = auth_util.fresh_secret()

  def __repr__(self):
    return '<School id={}, name={}, slug={}, domains={}>'.format(self.id, self.name, self.slug, self.domains)
