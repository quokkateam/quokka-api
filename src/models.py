import datetime
from slugify import slugify
from sqlalchemy.dialects.postgresql import JSON
from src import db
from src.helpers import auth_util


class User(db.Model):
  # TODO: combine email_verification_sent and email_verified into one Integer "status" column
  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String(120), index=True, unique=True)
  name = db.Column(db.String(120), nullable=False)
  hashed_pw = db.Column(db.String(120), nullable=True)
  email_verified = db.Column(db.Boolean(), default=False)
  email_verification_secret = db.Column(db.String(64))
  email_verification_sent = db.Column(db.Boolean(), default=False)
  school_id = db.Column(db.Integer, db.ForeignKey('school.id'), index=True, nullable=False)
  school = db.relationship('School', backref='users')
  is_admin = db.Column(db.Boolean(), default=False)
  reset_pw_secret = db.Column(db.String(64))
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
    return '<User id={}, email={}, name={}, email_verified={}, email_verification_sent={}, school_id={}, is_admin={}, is_destroyed={}, created_at={}>'.format(
      self.id, self.email, self.name, self.email_verified, self.email_verification_sent, self.school_id, self.is_admin, self.is_destroyed, self.created_at)


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
  is_demo = db.Column(db.Boolean(), default=False)
  is_destroyed = db.Column(db.Boolean(), default=False)
  created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

  def __init__(self, name, domains=[], is_demo=False):
    self.name = name
    self.slug = slugify(name, separator='-', to_lower=True)
    self.domains = domains
    self.is_demo = is_demo

  def __repr__(self):
    return '<School id={}, name={}, slug={}, domains={}, is_demo={}, is_destroyed={}, created_at={}>'.format(
      self.id, self.name, self.slug, self.domains, self.is_demo, self.is_destroyed, self.created_at)

  def active_users(self):
    return [u for u in self.users if not u.is_destroyed]

  def active_challenges(self):
    return [c for c in self.challenges if not c.is_destroyed]


class Challenge(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(120), nullable=False)
  slug = db.Column(db.String(120), index=True, nullable=False)
  school_id = db.Column(db.Integer, db.ForeignKey('school.id'), index=True, nullable=False)
  school = db.relationship('School', backref='challenges')
  check_in = db.relationship('CheckIn', uselist=False, back_populates='challenge')
  start_date = db.Column(db.DateTime)
  end_date = db.Column(db.DateTime)
  text = db.Column(db.Text)
  points = db.Column(db.Integer, default=0)
  suggestions = db.Column(JSON, default=[])
  is_destroyed = db.Column(db.Boolean(), default=False)
  created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

  def __init__(self, name=None, school=None, start_date=None, end_date=None, text=None, points=0, suggestions=None, slug=None):
    self.name = name
    self.slug = slug or slugify(name, separator='-', to_lower=True)
    self.school = school
    self.start_date = start_date
    self.end_date = end_date
    self.text = text
    self.points = points
    self.suggestions = suggestions or []

  def __repr__(self):
    return '<Challenge id={}, name={}, slug={}, school_id={}, start_date={}, end_date={}, text={}, points={}, suggestions={}, is_destroyed={}, created_at={}>'.format(
      self.id, self.name, self.slug, self.school_id, self.start_date, self.end_date, self.text, self.points, self.suggestions, self.is_destroyed, self.created_at)

  def active_prizes(self):
    return [p for p in self.prizes if not p.is_destroyed]


class Sponsor(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  school_id = db.Column(db.Integer, db.ForeignKey('school.id'), index=True, nullable=False)
  school = db.relationship('School', backref='sponsors')
  name = db.Column(db.String(120), nullable=False)
  logo = db.Column(db.String(240))
  url = db.Column(db.String(240))
  created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

  def __init__(self, school, name, logo=None, url=None):
    self.school = school
    self.name = name
    self.logo = logo
    self.url = url

  def __repr__(self):
    return '<Sponsor id={}, school_id={}, name={}, logo={}, url={}, created_at={}>'.format(
      self.id, self.school_id, self.name, self.logo, self.url, self.created_at)

  def active_prizes(self):
    return [p for p in self.prizes if not p.is_destroyed]


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
    return '<Prize id={}, challenge_id={}, sponsor_id={}, name={}, is_destroyed={}, created_at={}>'.format(
      self.id, self.challenge_id, self.sponsor_id, self.name, self.is_destroyed, self.created_at)


class CheckIn(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  challenge_id = db.Column(db.Integer, db.ForeignKey('challenge.id'), index=True, nullable=False)
  challenge = db.relationship('Challenge', back_populates='check_in')
  is_destroyed = db.Column(db.Boolean(), default=False)
  created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

  def __init__(self, challenge):
    self.challenge = challenge

  def __repr__(self):
    return '<CheckIn id={}, challenge_id={}, is_destroyed={}, created_at={}>'.format(
      self.id, self.challenge_id, self.is_destroyed, self.created_at)

  def active_check_in_questions(self):
    return [q for q in self.check_in_questions if not q.is_destroyed]


class CheckInQuestion(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  check_in_id = db.Column(db.Integer, db.ForeignKey('check_in.id'), index=True, nullable=False)
  check_in = db.relationship('CheckIn', backref='check_in_questions')
  text = db.Column(db.Text(), nullable=False)
  order = db.Column(db.Integer)
  is_destroyed = db.Column(db.Boolean(), default=False)
  created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

  def __init__(self, check_in, text, order):
    self.check_in = check_in
    self.text = text
    self.order = order

  def __repr__(self):
    return '<CheckInQuestion id={}, check_in_id={}, text={}, order={}, is_destroyed={}, created_at={}>'.format(
      self.id, self.check_in_id, self.text, self.order, self.is_destroyed, self.created_at)


class CheckInAnswer(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  check_in_question_id = db.Column(db.Integer, db.ForeignKey('check_in_question.id'), index=True, nullable=False)
  check_in_question = db.relationship('CheckInQuestion', backref='check_in_answers')
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True, nullable=False)
  user = db.relationship('User', backref='check_in_answers')
  text = db.Column(db.Text(), nullable=False)
  is_destroyed = db.Column(db.Boolean(), default=False)
  created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

  def __init__(self, user, text, check_in_question=None, check_in_question_id=None):
    if check_in_question_id:
      self.check_in_question_id = check_in_question_id
    else:
      self.check_in_question = check_in_question

    self.user = user
    self.text = text

  def __repr__(self):
    return '<CheckInAnswer id={}, check_in_question_id={}, user_id={}, text={}, is_destroyed={}, created_at={}>'.format(
      self.id, self.check_in_question_id, self.user_id, self.text, self.is_destroyed, self.created_at)