from src.mailers.client import send_email
from sendgrid.helpers.mail import Content


def complete_account(user):
  send_email(
    to=user.email,
    subject='Complete Your Account',
    content=Content('text/plain', 'Please complete your Quokka account!')
  )