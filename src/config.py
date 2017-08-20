import os
import subprocess

if os.environ.get('ENV') == 'prod':
    assert 'DATABASE_URL' in os.environ
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
else:
    if 'TEST_DB_URL' in os.environ:
        SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DB_URL')
    else:
        SQLALCHEMY_DATABASE_URI = subprocess.check_output(
                "heroku config --app quokka-api-test-db | grep DATABASE_URL | awk '{print $2}'",
                shell=True).decode('utf-8')
    DEBUG = True

SQLALCHEMY_TRACK_MODIFICATIONS = False

def get_pretty_config():
    import json
    return json.dumps(
        {k: v
         for (k, v) in globals().items() if k.isupper()},
        sort_keys=True,
        indent=2)
