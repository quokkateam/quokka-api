from flask_restplus import Api

api = Api(version='0.1', title='Quokka API')
namespace = api.namespace('api')

# Add all route handlers here:
from src.routes.user import *
from src.routes.school import *
from src.routes.inquiry import *