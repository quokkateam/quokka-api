import os

if os.environ.get('ENV') == 'prod':
    assert 'DATABASE_URL' in os.environ
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
else:
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/app.db'
    DEBUG = True

SQLALCHEMY_TRACK_MODIFICATIONS = False

def get_pretty_config():
    import json
    return json.dumps(
        {k: v
         for (k, v) in globals().items() if k.isupper()},
        sort_keys=True,
        indent=2)
