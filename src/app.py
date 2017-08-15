from flask import Flask

def create_app(config_file):
    app = Flask(__name__)
    app.config.from_pyfile(config_file)

    from models import db, migrate
    db.init_app(app)
    migrate.init_app(app, db)

    from routes import api
    api.init_app(app)

    return app

if __name__ == '__main__':
    create_app('config.py').run()
