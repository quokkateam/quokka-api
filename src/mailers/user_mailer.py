from src.mailers.client import send_email
from sendgrid.helpers.mail import Content


def complete_account(user, delay=True):
  return send_email(
    to=user.email,
    subject='Complete Your Account',
    template_vars={'name': user.name},
    delay=delay
  )