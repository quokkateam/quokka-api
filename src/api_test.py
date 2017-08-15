import json
import pytest

import email_client
from app import create_app
from models import db

@pytest.fixture
def app():
    app = create_app('test_config.py')
    return app

def test_create_user_flow(client, mocker):
    db.create_all()

    mocker.patch('email_client.send_verification_email')

    res = client.post('/api/users/', headers={'Content-Type': 'application/json'},
                      data=json.dumps(dict(email='e@mail.edu', password='hunter2')))

    assert res.json == dict(user_id=1, email='e@mail.edu')
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

    res = client.post('/api/verify_email/%d/%s' % (user.user_id, user.email_verification_secret))
    assert res.status_code == 200

    res = client.post('/api/mint_token', headers={'Content-Type': 'application/json'},
                      data=json.dumps(dict(email='e@mail.edu', password='hunter2')))

    assert 'token' in res.json
    assert res.status_code == 201

    db.drop_all()
