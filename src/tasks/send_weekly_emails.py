from operator import attrgetter
from src.models import School
from src import dbi, logger
from datetime import date
from src.mailers.challenge_mailer import weekly_challenge
from src.helpers.definitions import templates_dir
from markdown2 import markdown


def find_newly_started_challenge(school):
  challenges = sorted(school.active_challenges(), key=attrgetter('start_date'))

  start_dates = [c.start_date.date() for c in challenges]
  today = date.today()

  if today not in start_dates:
    return None

  week_index = start_dates.index(today)
  week_num = week_index + 1
  challenge = challenges[week_index]

  return challenge, week_num


def format_weekly_email_vars(challenge, week_num):
  prizes = []

  for p in challenge.prizes:
    sponsor = p.sponsor

    prizes.append({
      'prizeName': p.name,
      'sponsorName': sponsor.name,
      'sponsorLogo': sponsor.logo
    })

  return {
    'week_num': week_num,
    'name': challenge.name,
    'slug': challenge.slug,
    'challenge': markdown(challenge.text),
    'suggestions': challenge.suggestions,
    'prizes': prizes
  }

schools = dbi.find_all(School)

logger.info('Checking if weekly emails should be sent for {} schools...'.format(len(schools)))

for school in schools:
  challenge_info = find_newly_started_challenge(school)

  if not challenge_info:
    logger.info('Not today -- {}'.format(school.name))
    continue

  challenge, week_num = challenge_info

  logger.info('New Challenge Detected ({}) for {}...'.format(challenge.name, school.name))

  users = school.active_users()

  weekly_email_info = format_weekly_email_vars(challenge, week_num)

  logger.info('Sending emails to {} users at {}...'.format(len(users), school.name))

  template_path = '{}/challenge_mailer/weekly_challenges/{}.html'.format(templates_dir, challenge.slug)

  failures = []
  for user in users:
    success = weekly_challenge(user, weekly_email_info, template_path=template_path, delay=False)

    if not success:
      failures.append(user.email)

  logger.info('Emails Sent with {} Failures: {}'.format(len(failures), ','.join(failures)))

logger.info('DONE.')