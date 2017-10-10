from src.models import *
from src import dbi


def destroy_records(records):
  [dbi.destroy(r) for r in records]

print('Changing names to Self-Care...')
# Change name of 'Campus-Selected Challenge' to 'Self-Care'
cs_challenges = dbi.find_all(Challenge, {'slug': 'campus-selected-challenge'})
[dbi.update(c, {'name': 'Self-Care'}) for c in cs_challenges]

unc = dbi.find_one(School, {'slug': 'unc'})

if not unc:
  print('No School with slug, "unc".')
  exit()

challenges = [c for c in unc.challenges if c.slug in ['good-deeds', 'journaling']]

# Destroy the challenges (and dependent models through challenge) that UNC doesn't want
for c in challenges:
  print('Destroying appropriate records for {} challenge...'.format(c.slug))

  check_in = c.check_in
  check_in_questions = check_in.check_in_questions
  check_in_answers = []

  for q in check_in_questions:
    check_in_answers += q.check_in_answers

  destroy_records(c.prizes)
  destroy_records(check_in_answers)
  destroy_records(check_in_questions)

  dbi.destroy(check_in)
  dbi.destroy(c)