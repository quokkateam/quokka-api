from operator import attrgetter
from src import dbi
from src.models import CheckInAnswer


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