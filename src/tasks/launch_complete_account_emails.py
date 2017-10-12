from src import dbi, logger
from operator import attrgetter
from src.models import School
from src.mailers.user_mailer import complete_account
from time import sleep
from datetime import date


def find_launching_schools():
  launching = []

  for s in dbi.find_all(School, {'launchable': True}):
    challenges = sorted(s.active_challenges(), key=attrgetter('start_date'))

    if not challenges:
      continue

    if date.today() == challenges[0].start_date.date():
      launching.append(s)

  return launching


logger.info('Finding schools launching today...')

launching_schools = find_launching_schools()

if not launching_schools:
  logger.info('No schools launching today.')
  exit(0)

logger.info('Found {} schools that are launching today!'.format(len(launching_schools)))

for school in launching_schools:
  users_to_email = [u for u in school.users if not u.email_verification_sent]
  num_users = len(users_to_email)

  logger.info('Found {} users from {} to send email verification emails to.'.format(num_users, school.name))

  i = 0
  for user in users_to_email:
    if i % 10 == 0 and i > 0:
      logger.info('Done with {}/{}'.format(i, num_users))

    try:
      success = complete_account(user, delay=False)
    except BaseException:
      success = False
      logger.error('Error emailing user {}.'.format(user.email))

    if success:
      dbi.update(user, {'email_verification_sent': True})
    else:
      logger.error('Unsuccessful emailing user {}.'.format(user.email))

    sleep(0.3)  # Potential Rate-Limit protection for SendGrid API

    i += 1

logger.info('Done.')