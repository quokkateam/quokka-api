from flask import request
from src.helpers.auth_util import unserialize_token
from src.dbi import find_one
from src.models import Token


def set_current_user(func):
  def deco(*args, **kwargs):
    user_token = request.cookies.get('quokka-user')

    if not user_token:
      return '', 403

    token_info = unserialize_token(user_token)

    if not token_info.get('token_id') or not token_info.get('secret'):
      return '', 403

    token = find_one(Token, {
      'id': token_info['id'],
      'secret': token_info['secret']
    })

    if not token:
      return '', 403

    user = token.user

    if not user:
      return '', 403

    kwargs['user'] = user

    func(*args, **kwargs)

  return deco