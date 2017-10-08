from flask import request
from src.helpers.auth_util import unserialize_token
from src.dbi import find_one
from src.models import Token
from src.helpers import decode_url_encoded_str


def current_user():
  user_token = request.cookies.get('quokka-user')

  if not user_token:
    return None

  token_info = unserialize_token(decode_url_encoded_str(user_token))

  if not token_info.get('token_id') or not token_info.get('secret'):
    return None

  token = find_one(Token, {
    'id': token_info['token_id'],
    'secret': token_info['secret']
  })

  if not token:
    return None

  return token.user