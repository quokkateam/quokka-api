from flask_restplus import Resource
from src.routes import namespace, api
from src.helpers.user_helper import current_user
from src.helpers.check_in_helper import format_questions
from operator import attrgetter
from src import dbi, logger
from src.models import CheckIn, CheckInAnswer


@namespace.route('/check_in/<int:week_num>')
class GetCheckIn(Resource):
  """Fetch data for a user's check_in page by week number"""

  @namespace.doc('get_check_in')
  def get(self, week_num):
    user = current_user()

    if not user:
      return '', 403

    challenges = sorted(user.school.active_challenges(), key=attrgetter('start_date'))

    # Find the challenge requested by week index
    challenge = challenges[week_num - 1]

    # Get the CheckIn from the Challenge
    check_in = challenge.check_in

    # Get formatted question-answers for this user
    questions = format_questions(check_in, user)

    return {
      'id': check_in.id,
      'challengeName': challenge.name,
      'questions': questions
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