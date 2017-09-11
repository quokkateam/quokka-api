import sys
from argparse import ArgumentParser
from src.models import School, Challenge
from src.dbi import create, find_one, find_all
from src.challenges import universal_challenge_info
from operator import itemgetter
from datetime import datetime, timedelta

# Assuming kickoff is October 2nd
kickoff_date = datetime(2017, 10, 2, 0, 0)

if __name__ == '__main__':
  parser = ArgumentParser()
  parser.add_argument('--name', type=str, default=None)
  parser.add_argument('--domains', type=str, default=None)
  args = parser.parse_args(sys.argv[1:])

  if not args.name or not args.name.strip():
    print 'A name is required for the new school. Use the --name argument.'
    exit(0)

  if not args.domains:
    print 'Domains are required for a school. Use the --domains argument and pass a comma delimited string'
    exit(0)

  domains = [d.strip() for d in args.domains.split(',') if d.strip() != '']

  school = find_one(School, {'name':  args.name})

  if school:
    print 'School named {} already exists. Checking challenges...'.format(args.name)
  else:
    print 'Creating school, {}...'.format(args.name)
    school = create(School, {'name': args.name, 'domains': domains})

  sorted_challenges = sorted(universal_challenge_info.values(), key=itemgetter('defaultIndex'))

  challenges = find_all(Challenge, {'school': school})

  if len(challenges) == len(sorted_challenges):
    print 'Challenges already created for school.'
    exit(0)

  print 'Creating challenges for school...'

  for c in sorted_challenges:
    start_date = kickoff_date + timedelta(days=(7 * c['defaultIndex']))
    end_date = start_date + timedelta(days=6)

    create(Challenge, {
      'name': c['name'],
      'school': school,
      'start_date': start_date,
      'end_date': end_date
    })

  print 'Done!'