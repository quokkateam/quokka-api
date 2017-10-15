from src import dbi, logger
from src.models import School
from datetime import date, timedelta
from operator import attrgetter
from src.mailers.challenge_mailer import weekly_reminder
from time import sleep


def find_challenge_needing_reminder(school):
  challenges = sorted(school.active_challenges(), key=attrgetter('start_date'))
  today = date.today()

  i = 1
  for c in challenges:
    start_date = c.start_date.date()

    if today == start_date + timedelta(days=4):
      return c, i

    i += 1

  return None


def format_weekly_reminder_vars(challenge, week_num):
  days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

  return {
    'week_num': week_num,
    'challenge_name': challenge.name,
    'end_day': days[challenge.end_date.weekday()]
  }


schools = dbi.find_all(School, {'launchable': True})

logger.info('Checking if weekly reminder emails should be sent for {} schools...'.format(len(schools)))

for school in schools:
  challenge_info = find_challenge_needing_reminder(school)

  if not challenge_info:
    logger.info('Not today -- {}'.format(school.name))
    continue

  challenge, week_num = challenge_info

  logger.info('Challenge Needing Reminder Detected ({}) for {}...'.format(challenge.name, school.name))

  users = school.active_users()

  vars = format_weekly_reminder_vars(challenge, week_num)

  logger.info('Sending emails to {} users at {}...'.format(len(users), school.name))

  failures = []
  successes = []
  for user in users:
    try:
      vars['user_name'] = user.name
      success = weekly_reminder(user, vars, delay=False)
    except BaseException:
      success = False

    if success:
      successes.append(user.email)
    else:
      failures.append(user.email)

    sleep(0.3)  # Potential Rate-Limit protection for SendGrid API

  if failures:
    logger.info('Weekly Reminder Results for {}: Failures: {}; Successes: {}'.format(school.name, failures, successes))
  else:
    logger.info('All reminder emails sent successfully for {}.'.format(school.name))

logger.info('DONE.')