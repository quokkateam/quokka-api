from src.mailers.client import send_email


def weekly_challenge(user=None, vars={}, delay=True):
  return send_email(
    to=user.email,
    subject='Week {} Challenge'.format(vars.get('week_num')),
    template_vars=vars,
    delay=delay
  )


def congratulate_winner(challenge, prize, user, school=None, delay=True):
  if not school:
    school = user.school

  sponsor = prize.sponsor

  vars = {
    'name': user.name.split(' ')[0],
    'challenge_name': challenge.name,
    'sponsor_name': sponsor.name,
    'sponsor_logo': sponsor.logo,
    'prize_name': prize.name,
    'redeem_prize_email': school.redeem_prize_email
  }

  return send_email(
    to=user.email,
    subject='You won a prize!',
    template_vars=vars,
    delay=delay
  )


def weekly_reminder(user=None, vars={}, delay=True):
  return send_email(
    to=user.email,
    subject='Week {} Reminder'.format(vars.get('week_num')),
    template_vars=vars,
    delay=delay
  )
