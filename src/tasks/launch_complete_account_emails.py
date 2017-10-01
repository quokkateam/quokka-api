from src import dbi
from src.models import User
from src.mailers.user_mailer import complete_account
from time import sleep

users_to_email = dbi.find_all(User, {'email_verification_sent': False})
users_to_email = users_to_email + dbi.find_all(User, {'email_verification_sent': None})
num_users = len(users_to_email)

print('Found {} users to send email verification emails to.'.format(num_users))

i = 0
for user in users_to_email:
  if i % 10 == 0 and i > 0:
    print('Done with {}/{}'.format(i, num_users))

  try:
    success = complete_account(user, delay=False)
  except BaseException, e:
    success = False
    print('Error emailing user {}: {}'.format(user.email, e.__dict__))

  if success:
    dbi.update(user, {'email_verification_sent': True})
  else:
    print('Unsuccessful emailing user {}.'.format(user.email))

  sleep(0.5)
  i += 1

print('Done.')