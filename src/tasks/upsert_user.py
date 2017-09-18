import sys
from argparse import ArgumentParser
from src.models import School, User
from src import dbi
from src.helpers.user_validation import validate_user
from src.helpers.auth_util import hash_pw


def validate_arg(arg):
  if arg is None or (type(arg) == str and not arg.strip()):
    print('Argument {} required for script execution.'.format(arg))
    exit(0)


if __name__ == '__main__':
  parser = ArgumentParser()
  parser.add_argument('--school', type=str, default=None)
  parser.add_argument('--name', type=str, default=None)
  parser.add_argument('--email', type=str, default=None)
  parser.add_argument('--password', type=str, default=None)
  parser.add_argument('--admin', type=bool, default=None)

  args = parser.parse_args(sys.argv[1:])

  [validate_arg(getattr(args, a)) for a in ['school', 'name', 'email', 'password']]

  print('Finding school, {}...'.format(args.school))

  school = dbi.find_one(School, {'name':  args.school})

  if not school:
    print('No school named {}.'.format(args.school))
    exit(0)

  print('Finding user, {}...'.format(args.email))

  user = dbi.find_one(User, {
    'school': school,
    'email': args.email
  })

  if not user:
    print('No user for that email yet...creating new user...')

    if validate_user(args.email, school):
      print('Invalid email for school')
      exit(0)

    user = dbi.create(User, {
      'school': school,
      'name': args.name,
      'email': args.email
    })

  print('Updating name and password for user...')

  hashed_pw = hash_pw(args.password)

  dbi.update(user, {
    'name': args.name,
    'hashed_pw': hashed_pw,
    'is_admin': bool(args.admin)
  })

  print('Successfully upserted user!'.format(args.email))