from flask_restplus import Resource
from src.routes import namespace, api
from src.helpers.user_helper import current_user
from src.helpers.check_in_helper import *
from src.helpers.challenge_helper import current_week_num
from operator import attrgetter
from src import dbi, logger
from src.models import CheckIn, CheckInAnswer
from datetime import date


@namespace.route('/check_in/<int:week_num>')
class GetCheckIn(Resource):
  """Fetch data for a user's check_in page by week number"""

  @namespace.doc('get_check_in')
  def get(self, week_num):
    user = current_user()

    if not user:
      return '', 403

    challenges = sorted(user.school.active_challenges(), key=attrgetter('start_date'))

    curr_week_num = current_week_num(challenges)
    challenge = challenges[week_num - 1]

    # If requesting future check_in or
    # requesting first check_in but challenges haven't started yet, error out
    if week_num > curr_week_num or (week_num == 1 and date.today() < challenge.start_date.date()):
      return '', 403

    # Get the CheckIn from the Challenge
    check_in = challenge.check_in

    # Get formatted question-answers for this user
    questions = format_questions(check_in, user)

    return {
      'id': check_in.id,
      'challengeName': challenge.name,
      'questions': questions
    }


@namespace.route('/check_ins')
class GetCheckIns(Resource):
  """Fetch all school check_ins for /challenges#check-ins page"""

  @namespace.doc('get_check_ins_for_school')
  def get(self):
    user = current_user()

    if not user:
      return '', 403

    challenges = sorted(user.school.active_challenges(), key=attrgetter('start_date'))
    challenge_ids = [c.id for c in challenges]

    curr_week_num = current_week_num(challenges)

    # TODO: Eager-load all of this
    check_ins = dbi.find_all(CheckIn, {'challenge_id': challenge_ids})
    check_ins_map = {c.challenge_id: c for c in check_ins}

    check_in_answers_map = {a.check_in_question_id: a for a in user.check_in_answers}

    formatted_check_ins = []
    i = 1
    for c in challenges:
      check_in = check_ins_map[c.id]
      check_in_questions = check_in.check_in_questions
      num_questions = len(check_in_questions)

      num_answers = 0
      for q in check_in_questions:
        if check_in_answers_map.get(q.id):
          num_answers += 1

      data = {
        'challengeName': c.name,
        'weekNum': i,
        'numQuestions': num_questions,
        'numAnswers': num_answers
      }

      formatted_check_ins.append(data)
      i += 1

    launched = True
    if date.today() < challenges[0].start_date.date():
      launched = False

    return {
      'checkIns': formatted_check_ins,
      'weekNum': curr_week_num,
      'launched': launched
    }


@namespace.route('/check_in')
class SaveUserCheckIn(Resource):
  """Save a user's CheckIn"""

  @namespace.doc('save_user_check_in')
  def put(self):
    user = current_user()

    if not user:
      return '', 403

    payload = api.payload or {}

    check_in_id = payload.get('id')
    if not check_in_id:
      return 'CheckInId required to save user\'s answers', 500

    questions = payload.get('questions') or []
    if not questions:
      return 'Questions list required to save user\'s answers', 500

    check_in = dbi.find_one(CheckIn, {'id': check_in_id})

    if not check_in:
      logger.error('No CheckIn for id: {}'.format(check_in_id))
      return 'CheckIn Not Found', 500

    for q in questions:
      question = q.get('question')
      answer = q.get('answer')

      if not question or not answer or \
        not question.get('id') or not question.get('text') or 'text' not in answer:
        return 'Invalid question/answer format', 500

      answer_id = answer.get('id')

      # If answer already has been created, find and update it
      if answer_id:
        check_in_answer = dbi.find_one(CheckInAnswer, {'id': answer_id})

        if not check_in_answer:
          logger.error('No CheckInAnswer for id: {}'.format(answer_id))
          return 'Answer doesn\'t exist', 500

        dbi.update(check_in_answer, {'text': answer['text']})

      else: # otherwise, create a new answer
        dbi.create(CheckInAnswer, {
          'user': user,
          'check_in_question_id': question['id'],
          'text': answer['text']
        })

    questions = format_questions(check_in, user)

    return questions


@namespace.route('/check_ins/response_overviews')
class GetCheckInResponseOverviews(Resource):
  """Get response overviews for check_in responses"""

  @namespace.doc('get_check_in_response_overviews')
  def get(self):
    user = current_user()

    if not user or not user.is_admin:
      return '', 403

    challenges = sorted(user.school.active_challenges(), key=attrgetter('start_date'))

    resp = format_response_overviews(challenges)

    return resp


@namespace.route('/check_ins/responses/download/<int:check_in_id>')
class DownloadCheckInResponses(Resource):
  """Download Check-in responses"""

  @namespace.doc('download_check_in_responses')
  def get(self, check_in_id):
    user = current_user()

    if not user or not user.is_admin:
      return '', 403

    check_in = dbi.find_one(CheckIn, {'id': check_in_id})

    if not check_in:
      return '', 404

    csv_data = format_csv_responses(check_in)

    resp = {
      'content': csv_data,
      'filename': 'check-in-responses-{}.csv'.format(check_in.challenge.slug)
    }

    return resp