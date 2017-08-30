import datetime

from slugify import slugify
from sqlalchemy.dialects.postgresql import JSON

from src import db
from src.helpers import auth_util


class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String(120), index=True, unique=True)
  name = db.Column(db.String(120), nullable=False)
  hashed_pw = db.Column(db.String(120), nullable=True)
  email_verified = db.Column(db.Boolean(), default=False)
  email_verification_secret = db.Column(db.String(64))
  school_id = db.Column(db.Integer, db.ForeignKey('school.id'), index=True, nullable=False)
  # TODO make a helper for querying all live users
  is_destroyed = db.Column(db.Boolean(), default=False)
  created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
  school = db.relationship('School', backref='users')

  def __init__(self, email, name, school, hashed_pw=None):
    self.email = email
    self.name = name
    self.school = school
    self.hashed_pw = hashed_pw
    self.email_verification_secret = auth_util.fresh_secret()

  def __repr__(self):
    return '<User id={}, email={}, email_verified={}>'.format(
      self.id, self.email, self.email_verified)


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

  def __repr__(self):
    return '<School id={}, name={}, slug={}, domains={}>'.format(self.id, self.name, self.slug, self.domains)
