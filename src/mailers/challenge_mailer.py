from src.mailers.client import send_email


def weekly_challenge(user=None, vars={}, template_path=None, delay=True):
  return send_email(
    to=user.email,
    subject='Week {} Challenge'.format(vars.get('week_num')),
    template_vars=vars,
    template_path=template_path,
    delay=delay
  )


def congratulate_winner(challenge, user, delay=True):
  vars = {
    'name': user.name.split(' ')[0],
    'challenge_name': challenge.name,
  }

  return send_email(
    to=user.email,
    subject='You won a prize!',
    template_vars=vars,
    delay=delay
  )