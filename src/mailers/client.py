import sendgrid
import os
import re
from sendgrid.helpers.mail import Email, Mail
from src import delayed

sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))

email_override = os.environ.get('MAIL_TO_OVERRIDE')
perform_deliveries = bool(re.match('true', os.environ.get('MAILER_PERFORM_DELIVERIES') or '', re.I))


def send_email(to=None, subject=None, content=None, from_email='team@quokkachallenge.com'):
  delayed.add_job(perform, args=[to, subject, content, from_email])


def perform(to, subject, content, from_email):
  from_obj = Email(from_email, 'Quokka')
  to_obj = Email(email_override or to)
  mail = Mail(from_obj, subject, to_obj, content)

  if not perform_deliveries:
    print('Not sending email from {} to {} -- Mailer not configured to perform deliveries.'.format(
      from_obj.email, to_obj.email))
    return

  resp = sg.client.mail.send.post(request_body=mail.get())

  if resp.status_code not in [200, 202]:
    print('Email failed with error code {}: {}'.format(resp.status_code, resp.body))
    return False

  return True