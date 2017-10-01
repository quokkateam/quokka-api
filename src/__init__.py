import logging
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from src.config import get_config
from src.helpers.env import is_prod

# Create and configure the Flask app
app = Flask(__name__)
app.config.from_object(get_config())

# Set up logging
app.logger.addHandler(logging.FileHandler('main.log'))
app.logger.setLevel(logging.INFO)
logger = app.logger

# Create and start our delayed job scheduler
from src.scheduler import delayed
delayed.start()

# Set up Postgres DB
db = SQLAlchemy(app)

# Set up API routes
from src.routes import api
api.init_app(app)

# Require https if on prod
if is_prod() and os.environ.get('REQUIRE_SSL') == 'true':
  from flask_sslify import SSLify
  SSLify(app)