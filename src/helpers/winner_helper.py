from src.helpers.challenge_helper import current_week_num
from datetime import date


def formatted_winners(challenges):
  curr_week_num = current_week_num(challenges)
  launched = True

  if date.today() < challenges[0].start_date.date():
    launched = False

  resp = {
    'launched': launched,
    'weekNum': curr_week_num
  }

  winners_data = []
  i = 1
  for c in challenges:
    data = {
      'challenge': {
        'id': c.id,
        'name': c.name
      }
    }

    if i > curr_week_num:
      winners = []
    else:
      # unclear how winners are gonna be associated to prizes atm
      winners = [{'name': w.name, 'email': w.email} for w in c.winners]

    data['winners'] = winners

    winners_data.append(data)

    i += 1

  resp['winners'] = winners_data

  return resp