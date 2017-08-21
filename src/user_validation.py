# See https://github.com/quokkateam/quokka/blob/3af7fec346c63dec27c11a8c302de63841c3182e/src/utils/StatusCodes.js#L2
INVALID_EMAIL_DOMAIN = 1200
MALFORMED_EMAIL = 1201

def validate_user(email, school):
  """
  :returns: None if there is no error, or an error code if there is an error.
  >>> from models import School
  >>> validate_user('scroopy@noopers.edu', School('n', ['noopers.edu']))
  >>> validate_user('scroopy@noopers.edu', school=School('n', [])) == INVALID_EMAIL_DOMAIN
  True
  >>> validate_user('scroopynoopers.edu', school=School('n', [])) == MALFORMED_EMAIL
  True
  >>> validate_user('king@flippy@noopers.edu', school=School('n', [])) == MALFORMED_EMAIL
  True
  """
  if school is None:
    return INVALID_EMAIL_DOMAIN
  if not '@' in email:
    return MALFORMED_EMAIL
  parts = email.split('@')
  if len(parts) != 2:
    return MALFORMED_EMAIL
  (_, domain) = parts
  if domain not in school.domains:
    return INVALID_EMAIL_DOMAIN
  return None
