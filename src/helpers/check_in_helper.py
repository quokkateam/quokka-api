from operator import attrgetter
from src import dbi
from src.helpers.challenge_helper import current_week_num
from src.models import CheckInAnswer
from datetime import date
import json


def format_questions(check_in, user):
  check_in_questions = sorted(check_in.active_check_in_questions(), key=attrgetter('order'))
  check_in_question_ids = [q.id for q in check_in_questions]

  check_in_answers = []

  if check_in_question_ids:
    check_in_answers = dbi.find_all(CheckInAnswer, {
      'check_in_question_id': check_in_question_ids,
      'user': user
    })

  inline_answers = []
  for id in check_in_question_ids:
    answer = [a for a in check_in_answers if a.check_in_question_id == id]

    if answer:
      inline_answers.append(answer[0])
    else:
      inline_answers.append(None)

  questions = []
  i = 0
  for q in check_in_questions:
    check_in_answer = inline_answers[i]
    answer = None

    if check_in_answer:
      answer = {
        'id': check_in_answer.id,
        'text': check_in_answer.text
      }

    questions.append({
      'question': {
        'id': q.id,
        'text': q.text
      },
      'answer': answer
    })

    i += 1

  return questions


def format_response_overviews(challenges):
  curr_week_num = current_week_num(challenges)
  launched = True

  if date.today() < challenges[0].start_date.date():
    launched = False

  resp = {
    'launched': launched,
    'weekNum': curr_week_num
  }

  i = 1
  overviews = []
  for c in challenges:
    data = {
      'challenge': {
        'name': c.name,
        'slug': c.slug
      }
    }

    overview = {}
    if i <= curr_week_num:
      check_in = c.check_in

      check_in_answers = dbi.find_all(CheckInAnswer, {
        'check_in_question_id': [q.id for q in check_in.check_in_questions]
      })

      overview['checkInId'] = check_in.id
      overview['respCount'] = len(check_in_answers)

    data['overview'] = overview

    overviews.append(data)

    i += 1

  resp['weeklyResponses'] = overviews

  return resp


def format_csv_responses(check_in):
  questions = check_in.check_in_questions
  question_ids = []
  id2text = {}

  for q in questions:
    question_ids.append(q.id)
    id2text[q.id] = q.text

  answers = dbi.find_all(CheckInAnswer, {
    'check_in_question_id': [q.id for q in check_in.check_in_questions]
  })

  sorted_answers = sorted(answers, key=attrgetter('check_in_question_id'))

  content = ['question,answer']

  for a in sorted_answers:
    question = json.dumps(id2text.get(a.check_in_question_id))
    answer = json.dumps(a.text)
    row = ','.join([question, answer])
    content.append(row)

  return '\n'.join(content)