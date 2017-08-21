import json
import pytest

import email_client
from app import create_app
from models import db, User, School

@pytest.fixture
def app():
  app = create_app(config_file='test_config.py')
  return app

@pytest.yield_fixture(autouse=True)
def run_around_tests():
  try:
    db.create_all()

    school = School('University of School', ['uos.edu'])
    db.session.add(school)
    db.session.commit()

    yield

    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.drop_all()

def test_get_schools(client):
    res = client.get('/api/schools')
    assert res.status_code == 200

    assert res.json == dict(schools=[dict(
        name='University of School', slug='university-of-school', domains=['uos.edu'])])

def test_email_already_registered(client, mocker):
    mocker.patch('email_client.send_verification_email')

    res = client.post('/api/users/', headers={'Content-Type': 'application/json'},
                      data=json.dumps(dict(email='e@uos.edu', name='Scroopy', school='university-of-school', password='hunter2')))
    assert res.status_code == 201

    [user1] = User.query.all()

    res = client.post('/api/users/', headers={'Content-Type': 'application/json'},
                      data=json.dumps(dict(email='e@uos.edu', name='Noopers', school='university-of-school', password='hunter2')))
    assert res.status_code == 201

    [user2] = User.query.all()

    assert user1 == user2

def test_create_user_flow(client, mocker):
    mocker.patch('email_client.send_verification_email')

    res = client.post('/api/users/', headers={'Content-Type': 'application/json'},
                      data=json.dumps(dict(email='e@uos.edu', name='Scroopy', school='university-of-school', password='hunter2')))

    [user] = User.query.all()
    assert not user.email_verified
    assert 'id=1' in str(user)

    assert res.status_code == 201

    assert email_client.send_verification_email.called
    (user,), _ = email_client.send_verification_email.call_args

    res = client.post('/api/mint_token', headers={'Content-Type': 'application/json'},
                      data=json.dumps(dict(email='e@uos.edu', password='wrong password')))
    assert res.json['reason'] == 'Unrecognized credentials'
    assert res.status_code == 401

    res = client.post('/api/mint_token', headers={'Content-Type': 'application/json'},
                      data=json.dumps(dict(email='e@uos.edu', password='hunter2')))
    assert res.json['reason'] == 'email not verified'
    assert res.status_code == 401

    res = client.post('/api/verify_email/%d/%s' % (user.id, user.email_verification_secret))
    assert res.status_code == 200

    res = client.post('/api/mint_token', headers={'Content-Type': 'application/json'},
                      data=json.dumps(dict(email='e@uos.edu', password='hunter2')))

    assert 'token' in res.json
    assert res.status_code == 201

def test_create_user_no_password(client, mocker):
    mocker.patch('email_client.send_verification_email')

    res = client.post('/api/users/', headers={'Content-Type': 'application/json'},
                      data=json.dumps(dict(email='e@uos.edu', name='Scroopy', school='university-of-school')))

    [user] = User.query.all()
    assert not user.email_verified
    assert 'id=1' in str(user)

    assert res.status_code == 201

    assert email_client.send_verification_email.called
    (user,), _ = email_client.send_verification_email.call_args

    res = client.post('/api/mint_token', headers={'Content-Type': 'application/json'},
                      data=json.dumps(dict(email='e@uos.edu')))
    assert res.status_code == 400

    res = client.post('/api/mint_token', headers={'Content-Type': 'application/json'},
                      data=json.dumps(dict(email='e@uos.edu', password=[])))
    assert res.status_code == 400

    res = client.post('/api/mint_token', headers={'Content-Type': 'application/json'},
                      data=json.dumps(dict(email='e@uos.edu', password='')))
    assert res.json['reason'] == 'Unrecognized credentials'
    assert res.status_code == 401

    res = client.post('/api/mint_token', headers={'Content-Type': 'application/json'},
                      data=json.dumps(dict(email='e@uos.edu', password='hunter2')))
    assert res.json['reason'] == 'Unrecognized credentials'
    assert res.status_code == 401

    # Dummy hashed_pw in handler for this route is a hash of 'pw'. Test it.
    res = client.post('/api/mint_token', headers={'Content-Type': 'application/json'},
                      data=json.dumps(dict(email='e@uos.edu', password='pw')))
    assert res.json['reason'] == 'Unrecognized credentials'
    assert res.status_code == 401

    res = client.post('/api/verify_email/%d/%s' % (user.id, user.email_verification_secret))
    assert res.status_code == 200

    # Test again after email is verified.
    res = client.post('/api/mint_token', headers={'Content-Type': 'application/json'},
                      data=json.dumps(dict(email='e@uos.edu', password='pw')))
    assert res.json['reason'] == 'Unrecognized credentials'
    assert res.status_code == 401

def test_register_inquiry(client):
  # Ensure fails for no school
  res = client.post('/api/inquire', headers={'Content-Type': 'application/json'},
                    data=json.dumps(dict(email='e@uos.edu')))

  assert res.status_code == 400

  # Ensure fails for no email
  res = client.post('/api/inquire', headers={'Content-Type': 'application/json'},
                    data=json.dumps(dict(school='University of School')))

  assert res.status_code == 400

  # Ensure works for both email and school
  res = client.post('/api/inquire', headers={'Content-Type': 'application/json'},
                    data=json.dumps(dict(email='e@uos.edu', school='University of School')))

  assert res.status_code == 200