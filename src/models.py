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
  school = db.relationship('School', backref='users')
  is_admin = db.Column(db.Boolean(), default=False)
  is_destroyed = db.Column(db.Boolean(), default=False)
  created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

  def __init__(self, email, name, school, hashed_pw=None, is_admin=False):
    self.email = email
    self.name = name
    self.school = school
    self.hashed_pw = hashed_pw
    self.is_admin = is_admin
    self.email_verification_secret = auth_util.fresh_secret()

  def __repr__(self):
    return '<User id={}, email={}, name={}, email_verified={}, school_id={}, is_admin={}, is_destroyed={}, created_at={}>'.format(
      self.id, self.email, self.name, self.email_verified, self.school_id, self.is_admin, self.is_destroyed, self.created_at)


class Token(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True, nullable=False)
  secret = db.Column(db.String(64))
  user = db.relationship('User', backref='tokens')

  def __init__(self, user, secret):
    self.user = user
    self.secret = secret

  def __repr__(self):
    return '<Token id={}, user_id={}>'.format(self.id, self.user_id)


class School(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(120), unique=True)
  slug = db.Column(db.String(120), index=True)
  domains = db.Column(JSON, default=[])
  is_destroyed = db.Column(db.Boolean(), default=False)
  created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

  def __init__(self, name, domains=[]):
    self.name = name
    self.slug = slugify(name, separator='-', to_lower=True)
    self.domains = domains

  def __repr__(self):
    return '<School id={}, name={}, slug={}, domains={}, is_destroyed={}, created_at={}>'.format(
      self.id, self.name, self.slug, self.domains, self.is_destroyed, self.created_at)


class Challenge(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(120), nullable=False)
  slug = db.Column(db.String(120), index=True, nullable=False)
  school_id = db.Column(db.Integer, db.ForeignKey('school.id'), index=True, nullable=False)
  school = db.relationship('School', backref='challenges')
  start_date = db.Column(db.DateTime)
  end_date = db.Column(db.DateTime)
  text = db.Column(db.Text)
  points = db.Column(db.Integer, default=0)
  suggestions = db.Column(JSON, default=[])
  is_destroyed = db.Column(db.Boolean(), default=False)
  created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

  def __init__(self, name, school, start_date=None, end_date=None, text=None, points=0, suggestions=[]):
    self.name = name
    self.slug = slugify(name, separator='-', to_lower=True)
    self.school = school
    self.start_date = start_date
    self.end_date = end_date
    self.text = text
    self.points = points
    self.suggestions = suggestions

  def __repr__(self):
    return '<Challenge id={}, name={}, slug={}, school_id={}, start_date={}, end_date={}, text={}, points={}, suggestions={}, is_destroyed={}, created_at={}>'.format(
      self.id, self.name, self.slug, self.school_id, self.start_date, self.end_date, self.text, self.points, self.suggestions, self.is_destroyed, self.created_at)


class Sponsor(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  school_id = db.Column(db.Integer, db.ForeignKey('school.id'), index=True, nullable=False)
  school = db.relationship('School', backref='sponsors')
  name = db.Column(db.String(120), nullable=False)
  logo = db.Column(db.String(240))
  created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

  def __init__(self, school, name, logo=None):
    self.school = school
    self.name = name
    self.logo = logo

  def __repr__(self):
    return '<Sponsor id={}, school_id={}, name={}, logo={}, created_at={}>'.format(
      self.id, self.school_id, self.name, self.logo, self.created_at)


class Prize(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  challenge_id = db.Column(db.Integer, db.ForeignKey('challenge.id'), index=True, nullable=False)
  challenge = db.relationship('Challenge', backref='prizes')
  sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.id'), index=True, nullable=False)
  sponsor = db.relationship('Sponsor', backref='prizes')
  name = db.Column(db.String(240), nullable=False)
  is_destroyed = db.Column(db.Boolean(), default=False)
  created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

  def __init__(self, challenge, sponsor, name):
    self.challenge = challenge
    self.sponsor = sponsor
    self.name = name

  def __repr__(self):
    return '<Sponsor id={}, challenge_id={}, sponsor_id={}, name={}, is_destroyed={}, created_at={}>'.format(
      self.id, self.challenge_id, self.sponsor_id, self.name, self.is_destroyed, self.created_at)