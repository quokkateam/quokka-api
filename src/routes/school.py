from flask_restplus import Resource
from src.models import School
from src.routes import namespace, json_response
import src.dbi as dbi

@namespace.route('/schools')
class GetSchools(Resource):
  """Fetch all non-destroyed Schools"""

  @namespace.doc('get_schools')
  def get(self):
    schools = dbi.find_all(School)
    school_data = [{'name': s.name, 'slug': s.slug, 'domains': s.domains} for s in schools]

    return json_response({'schools': school_data}), 200