from app import create_app
from flask_migrate import MigrateCommand
from flask_script import Manager

manager = Manager(create_app)
manager.add_option("-c", "--config", dest="config_module", required=False)
manager.add_command('db', MigrateCommand)
