import sendgrid
import os
import re
import inspect
from sendgrid.helpers.mail import *
from src import delayed, logger
from src.helpers.definitions import templates_dir
from src.helpers.template_helper import template_as_str

sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))

email_override = os.environ.get('MAIL_TO_OVERRIDE')
perform_deliveries = bool(re.match('true', os.environ.get('MAILER_PERFORM_DELIVERIES') or '', re.I))


def send_email(to=None, subject=None, from_email='team@quokkachallenge.com', template_vars={}, delay=True):
  template = None

  try:
    stack = inspect.stack()
    caller = stack[1]
    mailer = caller[1].split('/')[-1][:-3]
    method = caller[3]

    template_path = '{}/{}/{}.html'.format(templates_dir, mailer, method)

    if not os.path.exists(template_path):
      logger.error('Error finding template at {}. Not sending email.'.format(template_path))
      return False

    template = template_as_str(template_path, template_vars)
  except BaseException:
    logger.error('Error configuring email template')
    return False

  if not template:
    logger.error('Empty template for caller: {}. Not sending email.'.format(inspect.stack()[1]))
    return False

  content = Content('text/html', template)

  if delay:
    delayed.add_job(perform, args=[to, subject, content, from_email])
    return True
  else:
    return perform(to, subject, content, from_email)


def perform(to, subject, content, from_email):
  from_obj = Email(from_email, 'Quokka')
  to_obj = Email(email_override or to)
  mail = Mail(from_obj, subject, to_obj, content)

  if not perform_deliveries:
    logger.warn('Not sending email from {} to {} -- Mailer not configured to perform deliveries.'.format(
      from_obj.email, to_obj.email))
    return False

  try:
    logger.info('Sending email from {} to {}...'.format(from_obj.email, to_obj.email))
    resp = sg.client.mail.send.post(request_body=mail.get())
  except BaseException:
    logger.error('Error sending email to {}'.format(to_obj.email))
    return False

  if resp.status_code not in [200, 202]:
    print('Email failed with error code {}: {}'.format(resp.status_code, resp.body))
    return False

  logger.info('Successfully sent email.')
  return True