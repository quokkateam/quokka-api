from src.models import *
from src import dbi

school = dbi.find_one(School, {'slug': 'duke-university'})

challenges = [c for c in school.challenges if c.slug in ['positivity-mindfulness', 'journaling']]

check_ins = [c.check_in for c in challenges]

questions = []
for c in check_ins:
  questions += c.check_in_questions

answers = []
for q in questions:
  answers += q.check_in_answers

prizes = []
for c in challenges:
  prizes += c.prizes

models = prizes + answers + questions + check_ins + challenges

for m in models:
  dbi.destroy(m)