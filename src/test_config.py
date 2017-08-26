import os
import subprocess

DEBUG = True
if 'TEST_DB_URL' in os.environ:
  SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DB_URL')
else:
  if 'TEST_DB_URL' in os.environ:
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DB_URL')
  else:
    SQLALCHEMY_DATABASE_URI = subprocess.check_output(
      "heroku config --app quokka-api-test-db | grep DATABASE_URL | awk '{print $2}'",
      shell=True).decode('utf-8')
SQLALCHEMY_TRACK_MODIFICATIONS = False
