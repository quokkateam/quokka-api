from operator import attrgetter
from src.models import School, User
from src import dbi, logger
from datetime import date
from src.mailers.challenge_mailer import weekly_challenge
from markdown2 import markdown
from src.challenges import universal_challenge_info


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
      'prize_name': p.name,
      'sponsor_name': sponsor.name,
      'sponsor_logo': sponsor.logo
    })

  check_in_questions = [q.text for q in challenge.check_in.check_in_questions]

  universal_challenge = universal_challenge_info.get(challenge.slug)

  static_email_content = universal_challenge.get('email')

  if not static_email_content:
    logger.error('No static email content for this Challenge({})'.format(challenge.id))
    exit(1)

  science = static_email_content.get('science')
  welcome_text = static_email_content.get('welcome_text')

  if not science or not welcome_text:
    logger.error('Science or Welcome Text not configured in static email content for Challenge({})'.format(challenge.id))
    exit(1)

  if not challenge.text:
    logger.error('No text for Challenge({}). Not sending emails'.format(challenge.id))
    exit(1)

  suggestions = [markdown(s) for s in challenge.suggestions]

  return {
    'week_num': week_num,
    'name': challenge.name,
    'slug': challenge.slug,
    'challenge': markdown(challenge.text),
    'suggestions': suggestions,
    'prizes': prizes,
    'check_in_questions': check_in_questions,
    'science': science,
    'welcome_text': welcome_text
  }


school = dbi.find_one(School, {'slug': 'tufts-university'})

challenge_info = find_newly_started_challenge(school)

if not challenge_info:
  logger.info('Not today -- {}'.format(school.name))
  exit()

challenge, week_num = challenge_info

logger.info('New Challenge Detected ({}) for {}...'.format(challenge.name, school.name))

weekly_email_info = format_weekly_email_vars(challenge, week_num)

user = dbi.find_one(User, {'email': 'benwhittle31@gmail.com'})

try:
  success = weekly_challenge(user, weekly_email_info, delay=False)
except BaseException:
  logger.error('FAILED')

logger.info('DONE.')