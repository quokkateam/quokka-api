import json
import pytest

import email_client
from app import create_app
from models import db, User

@pytest.fixture
def app():
    app = create_app(config_file='test_config.py')
    return app

def test_email_already_registered(client, mocker):
    db.create_all()

    mocker.patch('email_client.send_verification_email')

    res = client.post('/api/users/', headers={'Content-Type': 'application/json'},
                      data=json.dumps(dict(email='e@mail.edu', password='hunter2')))
    assert res.status_code == 201

    [user1] = User.query.all()

    res = client.post('/api/users/', headers={'Content-Type': 'application/json'},
                      data=json.dumps(dict(email='e@mail.edu', password='hunter2')))
    assert res.status_code == 201

    [user2] = User.query.all()

    assert user1 == user2

    db.drop_all()

def test_create_user_flow(client, mocker):
    db.create_all()

    mocker.patch('email_client.send_verification_email')

    res = client.post('/api/users/', headers={'Content-Type': 'application/json'},
                      data=json.dumps(dict(email='e@mail.edu', password='hunter2')))

    [user] = User.query.all()
    assert not user.email_verified
    assert 'id=1' in str(user)

    assert res.json == dict(id=1, email='e@mail.edu')
    assert res.status_code == 201

    assert email_client.send_verification_email.called
    (user,), _ = email_client.send_verification_email.call_args

    res = client.post('/api/mint_token', headers={'Content-Type': 'application/json'},
                      data=json.dumps(dict(email='e@mail.edu', password='wrong password')))
    assert res.json['reason'] == 'Unrecognized credentials'
    assert res.status_code == 401

    res = client.post('/api/mint_token', headers={'Content-Type': 'application/json'},
                      data=json.dumps(dict(email='e@mail.edu', password='hunter2')))
    assert res.json['reason'] == 'email not verified'
    assert res.status_code == 401

    res = client.post('/api/verify_email/%d/%s' % (user.id, user.email_verification_secret))
    assert res.status_code == 200

    res = client.post('/api/mint_token', headers={'Content-Type': 'application/json'},
                      data=json.dumps(dict(email='e@mail.edu', password='hunter2')))

    assert 'token' in res.json
    assert res.status_code == 201

    db.drop_all()
