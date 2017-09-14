from src import db

db.engine.execute('DROP TABLE IF EXISTS alembic_version;')