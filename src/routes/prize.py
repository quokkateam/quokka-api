from flask_restplus import Resource, fields
from flask import request
from src.models import Prize, Challenge, Sponsor
from src.helpers.prize_helper import format_prizes
from src.routes import namespace, api
from src.helpers.user_helper import current_user
from src import dbi

create_prize_model = api.model('Prize', {
  'challengeId': fields.Integer(required=True),
  'sponsorId': fields.Integer(required=True),
  'name': fields.String(required=True)
})

update_prize_model = api.model('Prize', {
  'id': fields.Integer(required=True),
  'sponsorId': fields.Integer(required=True),
  'name': fields.String(required=True)
})


@namespace.route('/prize')
class RestfulPrize(Resource):

  @namespace.doc('create_prize')
  @namespace.expect(create_prize_model, validate=True)
  def post(self):
    user = current_user()

    if not user or not user.is_admin:
      return '', 403

    challenge = dbi.find_one(Challenge, {'id': api.payload['challengeId']})

    if not challenge:
      return 'Challenge required to create prize', 500

    sponsor = dbi.find_one(Sponsor, {'id': api.payload['sponsorId']})

    if not sponsor:
      return 'Sponsor required to create prize', 500

    dbi.create(Prize, {
      'challenge': challenge,
      'sponsor': sponsor,
      'name': api.payload['name']
    })

    return format_prizes(challenge.active_prizes())

  @namespace.doc('update_prize')
  @namespace.expect(update_prize_model, validate=True)
  def put(self):
    user = current_user()

    if not user or not user.is_admin:
      return '', 403

    prize = dbi.find_one(Prize, {'id': api.payload['id']})

    if not prize:
      return 'Can\'t find prize to update :/', 500

    sponsor = dbi.find_one(Sponsor, {'id': api.payload['sponsorId']})

    if not sponsor:
      return 'Sponsor required to update prize', 500

    dbi.update(prize, {
      'sponsor': sponsor,
      'name': api.payload['name']
    })

    prizes = format_prizes(prize.challenge.active_prizes())

    return prizes, 200


  @namespace.doc('destroy_prize')
  def delete(self):
    user = current_user()

    if not user or not user.is_admin:
      return '', 403

    args = dict(request.args.items())
    prize = dbi.find_one(Prize, {'id': args.get('id')})

    if not prize:
      return 'Can\'t find prize to destroy :/', 500

    dbi.destroy(prize)

    prizes = format_prizes(prize.challenge.active_prizes())

    return prizes, 200