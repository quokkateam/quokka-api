from src.models import *
from src import dbi
from src.challenges import universal_challenge_info

school = dbi.find_one(School, {'slug': 'rice-university'})

challenges = school.active_challenges()

for challenge in challenges:
  check_in = challenge.check_in

  if not check_in:
    continue

  if len(check_in.check_in_questions) > 0:
    continue

  universal_challenge = universal_challenge_info.get(challenge.slug)

  if not universal_challenge:
    continue

  questions = universal_challenge['check_in_questions']

  i = 0
  for q in questions:
    print('Creating CheckInQuestion...')

    dbi.create(CheckInQuestion, {
      'check_in': check_in,
      'text': q,
      'order': i
    })

    i += 1