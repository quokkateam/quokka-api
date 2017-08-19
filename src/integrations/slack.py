import os
import requests


def log_inquiry(school, email):
  webhook_url = os.environ.get('SLACK_INQUIRY_WEBHOOK')

  if not webhook_url:
    print 'Not sending new inquiry to Slack...webhook env var not set'
    return

  message = '*New Inquiry*\nSchool: {}\nEmail: {}'.format(school, email)

  try:
    resp = requests.post(webhook_url,
                             json={'text': message},
                             headers={'Content-Type': 'application/json'})

    if resp.status_code != 200:
      raise ValueError(resp.text)

  except BaseException, e:
    print 'Slack Error: {}'.format(e)