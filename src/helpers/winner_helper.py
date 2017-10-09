from src.helpers.challenge_helper import current_week_num
from datetime import date
from src import dbi
from src.models import User


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

    user_info = []
    if i <= curr_week_num:
      prizes = c.prizes

      if prizes:
        for p in prizes:
          winners = p.winners

          if not winners:
            continue

          users = dbi.find_all(User, {'id': [w.user_id for w in winners]})

          sponsor = p.sponsor

          for u in users:
            user_info.append({
              'user': {
                'name': u.name,
                'email': u.email
              },
              'prize': {
                'name': p.name
              },
              'sponsor': {
                'name': sponsor.name,
                'logo': sponsor.logo
              }
            })
      else:
        data['noPrizes'] = True

    data['winners'] = user_info

    winners_data.append(data)

    i += 1

  resp['winners'] = winners_data

  return resp