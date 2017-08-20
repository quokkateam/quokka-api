from flask import Flask


def create_app(config_file='config.py'):
  app = Flask(__name__)
  app.config.from_pyfile(config_file)

  from models import db, migrate
  db.init_app(app)
  migrate.init_app(app, db)

  from routes import api
  api.init_app(app)

  from flask_sslify import SSLify
  SSLify(app)

  return app


if __name__ == '__main__':
  # Bind to PORT if defined, otherwise default to 5000.
  import os
  port = int(os.environ.get('PORT', 5000))
  create_app().run(host='0.0.0.0', port=port)
