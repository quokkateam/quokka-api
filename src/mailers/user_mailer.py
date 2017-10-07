from src.mailers.client import send_email
from src.config import get_config
from src.helpers import url_encode_str

config = get_config()


def complete_account(user, delay=True):
  encoded_secret = url_encode_str(user.email_verification_secret)
  link = '{}/verify-email/{}/{}'.format(config.URL, user.id, encoded_secret)

  vars = {
    'name': user.name.split(' ')[0],
    'link': link
  }

  return send_email(
    to=user.email,
    subject='Complete Your Account',
    template_vars=vars,
    delay=delay
  )


def reset_password(user, delay=True):
  encoded_secret = url_encode_str(user.reset_pw_secret)
  link = '{}/forgot-pw/{}/{}'.format(config.URL, user.id, encoded_secret)

  vars = {
    'name': user.name.split(' ')[0],
    'link': link
  }

  return send_email(
    to=user.email,
    subject='Reset Your Password',
    template_vars=vars,
    delay=delay
  )


def invite_user(from_user, to_email, delay=True):
  vars = {
    'from_user_name': from_user.name,
    'school_name': from_user.school.name
  }

  return send_email(
    to=to_email,
    subject='You\'ve been invited to join Quokka!',
    template_vars=vars,
    delay=delay
  )