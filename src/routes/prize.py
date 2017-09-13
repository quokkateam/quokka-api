from flask_restplus import Resource, fields
from src.models import Prize, Challenge, Sponsor
from src.helpers.challenge_helper import format_prizes
from src.routes import namespace, api
from src import dbi

create_prize_model = api.model('Prize', {
  'challengeId': fields.Integer(),
  'sponsorId': fields.Integer(),
  'name': fields.String()
})

update_prize_model = api.model('Prize', {
  'id': fields.Integer(),
  'sponsorId': fields.Integer(),
  'name': fields.String()
})

destroy_prize_model = api.model('Prize', {
  'id': fields.Integer()
})


@namespace.route('/prize')
class RestfulPrize(Resource):

  @namespace.doc('create_prize')
  @namespace.marshal_with(create_prize_model)
  def post(self):
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

    prizes = format_prizes(challenge.prizes)

    return prizes, 201

  @namespace.doc('update_prize')
  @namespace.marshal_with(update_prize_model)
  def put(self):
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

    prizes = format_prizes(prize.challenge.prizes)

    return prizes, 200


  @namespace.doc('destroy_prize')
  @namespace.marshal_with(destroy_prize_model)
  def delete(self):
    prize = dbi.find_one(Prize, {'id': api.payload['id']})

    if not prize:
      return 'Can\'t find prize to destroy :/', 500

    dbi.destroy(prize)

    prizes = format_prizes(prize.challenge.prizes)

    return prizes, 200