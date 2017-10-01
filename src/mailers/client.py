import sendgrid
import os
import re
import inspect
from sendgrid.helpers.mail import *
from src import delayed, logger
from src.mailers import templates_map

sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
email_override = os.environ.get('MAIL_TO_OVERRIDE')
perform_deliveries = bool(re.match('true', os.environ.get('MAILER_PERFORM_DELIVERIES') or '', re.I))


def send_email(to=None, subject=None, content=None, from_email='team@quokkachallenge.com', template_vars=None):
  template_id = None

  try:
    stack = inspect.stack()
    caller = stack[1]
    mailer = caller[1].split('/')[-1].replace('_mailer.py', '')
    method = caller[3]
    template_id = templates_map.get('{}:{}'.format(mailer, method))
  except BaseException:
    logger.error('Error finding template_id from stack')

  delayed.add_job(perform, args=[to, subject, content, from_email, template_id, template_vars])


def perform(to, subject, content, from_email, template_id, template_vars):
  from_obj = Email(from_email, 'Quokka')
  to_obj = Email(email_override or to)

  if not content:
    content = Content('text/plain', 'text')

  mail = Mail(from_obj, subject, to_obj, content)

  if template_id:
    mail.template_id = template_id

    if template_vars:
      prz = mail.personalizations[0]

      for k, v in template_vars.iteritems():
        prz.add_substitution(Substitution('%{}%'.format(k), v))

      mail.add_personalization(prz)

  if not perform_deliveries:
    logger.warn('Not sending email from {} to {} -- Mailer not configured to perform deliveries.'.format(
      from_obj.email, to_obj.email))
    return

  logger.info('Sending email from {} to {}...'.format(from_obj.email, to_obj.email))

  try:
    resp = sg.client.mail.send.post(request_body=mail.get())
  except BaseException, e:
    print('Email failed')
    print(e.__dict__)

  if resp.status_code not in [200, 202]:
    print('Email failed with error code {}: {}'.format(resp.status_code, resp.body))
    return False

  logger.info('Successfully sent email')

  return True