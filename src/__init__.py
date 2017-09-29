import logging
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from src.config import get_config
from src.helpers.env import is_prod
from src.send_mail import send_test_email_to_andrew

app = Flask(__name__)
app.config.from_object(get_config())

app.logger.addHandler(logging.FileHandler('main.log'))
app.logger.setLevel(logging.INFO)
logger = app.logger

db = SQLAlchemy(app)

from src.routes import api
api.init_app(app)

if is_prod() and os.environ.get('REQUIRE_SSL') == 'true':
  from flask_sslify import SSLify
  SSLify(app)

from src.scheduler import delayed
delayed.start()

delayed.add_job(send_test_email_to_andrew)
