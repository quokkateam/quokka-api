from src.mailers.client import send_email
from src.config import get_config
from src.helpers import url_encode_str

config = get_config()


def complete_account(user, delay=True):
  return send_email(
    to=user.email,
    subject='Complete Your Account',
    template_vars={'name': user.name},
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
    subject='BLah Your Password',
    template_vars=vars,
    delay=delay
  )