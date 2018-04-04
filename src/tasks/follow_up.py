from src.models import School
from src import dbi, logger
from src.mailers.user_mailer import follow_up_email
from time import sleep


# schools = dbi.find_all(School, {'launchable': True})

# for school in schools:
#   users = school.active_users()

#   logger.info('Sending emails to {} users at {}...'.format(len(users), school.name))

#   failures = []
#   successes = []
#   for user in users:
#     try:
#       success = follow_up_email(user, delay=False)
#     except BaseException:
#       success = False

#     if success:
#       successes.append(user.email)
#     else:
#       failures.append(user.email)

#     sleep(0.3)  # Potential Rate-Limit protection for SendGrid API

#   if failures:
#     logger.info('Weekly Email Results for {}: Failures: {}; Successes: {}'.format(school.name, failures, successes))
#   else:
#     logger.info('All emails sent successfully for {}.'.format(school.name))

# logger.info('DONE.')