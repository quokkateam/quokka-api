from flask_restplus import Api

api = Api(version='0.1', title='Quokka API')
namespace = api.namespace('api')