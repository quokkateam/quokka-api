import sys
from argparse import ArgumentParser
from src.models import School, Challenge, CheckIn, CheckInQuestion
from src.dbi import create, find_one, find_all, update
from src.challenges import universal_challenge_info
from operator import itemgetter
from datetime import datetime, timedelta

kickoff_date = datetime(2017, 10, 16, 0, 0)

if __name__ == '__main__':
  parser = ArgumentParser()
  parser.add_argument('--name', type=str, default=None)
  parser.add_argument('--domains', type=str, default=None)
  args = parser.parse_args(sys.argv[1:])

  if not args.name or not args.name.strip():
    print('A name is required for the new school. Use the --name argument.')
    exit(0)

  school = find_one(School, {'name':  args.name})

  domains = None
  if args.domains:
    domains = [d.strip() for d in args.domains.split(',') if d.strip() != '']

  if school:
    print('School named {} already exists.'.format(args.name))

    if domains:
      school = update(school, {'domains': domains})
  else:
    # NOTE: Since most schools added to the DB early on were added manually without a created_at,
    # this will probably blow up with an error saying there's an issue with primary_key not being unique...
    # This is because it somehow doesn't "see" the other school records that were manually added and then
    # tries to create this record with a primary_id of 1, which obviously won't work. Options at this point:
    # (1) See if adding fake created_at datetimes for the schools that don't have them will fix this.
    # (2) Add the school with a SQL INSERT before running this script
    print('Creating school, {}...'.format(args.name))

    if not domains:
      print('Domains are required to create a new school. Use the --domains argument.')
      exit(0)

    school = create(School, {'name': args.name, 'domains': domains})

  sorted_challenges = []
  for k, v in universal_challenge_info.items():
    if v.get('custom'):
      continue

    v['slug'] = k
    sorted_challenges.append(v)

  sorted_challenges = sorted(sorted_challenges, key=itemgetter('defaultIndex'))

  challenges = find_all(Challenge, {'school': school})

  print('Creating challenges for school...')

  # For each challenge listed in challenges.py...
  for c in sorted_challenges:
    start_date = kickoff_date + timedelta(days=(7 * c['defaultIndex']))
    end_date = start_date + timedelta(days=6)

    # Find or create a Challenge
    challenge = find_one(Challenge, {'name': c['name'], 'school': school})

    if not challenge:
      print('Creating Challenge: {}...'.format(c['name']))

      challenge = create(Challenge, {
        'name': c['name'],
        'slug': c['slug'],
        'school': school,
        'start_date': start_date,
        'end_date': end_date
      })

    # Find or create a new CheckIn for this Challenge
    check_in = find_one(CheckIn, {'challenge': challenge})

    if not check_in:
      print('Creating CheckIn for Challenge: {}...'.format(c['name']))
      check_in = create(CheckIn, {'challenge': challenge})

    # Find or create new CheckInQuestions for this CheckIn
    questions = c['check_in_questions']

    i = 0
    for q in questions:
      check_in_question = find_one(CheckInQuestion, {
        'check_in': check_in,
        'text': q
      })

      if not check_in_question:
        print('Creating CheckInQuestion...')

        create(CheckInQuestion, {
          'check_in': check_in,
          'text': q,
          'order': i
        })

      i += 1

  print('Done!')