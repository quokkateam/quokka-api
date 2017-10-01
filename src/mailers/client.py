import sendgrid
import os
import re
import inspect
from sendgrid.helpers.mail import *
from src import delayed, logger
from src.helpers.definitions import templates_dir
from mako.template import Template

sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))

email_override = os.environ.get('MAIL_TO_OVERRIDE')
perform_deliveries = bool(re.match('true', os.environ.get('MAILER_PERFORM_DELIVERIES') or '', re.I))


def send_email(to=None, subject=None, from_email='team@quokkachallenge.com', template_vars={}):
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

    t = Template(filename=template_path)
    template = t.render(**template_vars)
  except BaseException, e:
    logger.error('Error configuring email template, {}'.format(e.__dict__))
    return False

  if not template:
    logger.error('Empty template for caller: {}. Not sending email.'.format(inspect.stack()[1]))
    return False

  content = Content('text/html', template)

  delayed.add_job(perform, args=[to, subject, content, from_email])

  return True


def perform(to, subject, content, from_email):
  from_obj = Email(from_email, 'Quokka')
  to_obj = Email(email_override or to)
  mail = Mail(from_obj, subject, to_obj, content)

  if not perform_deliveries:
    logger.warn('Not sending email from {} to {} -- Mailer not configured to perform deliveries.'.format(
      from_obj.email, to_obj.email))
    return

  try:
    logger.info('Sending email from {} to {}...'.format(from_obj.email, to_obj.email))
    resp = sg.client.mail.send.post(request_body=mail.get())
  except BaseException, e:
    print('Email failed: {}'.format(e.__dict__))
    return

  if resp.status_code not in [200, 202]:
    print('Email failed with error code {}: {}'.format(resp.status_code, resp.body))
    return

  logger.info('Successfully sent email.')