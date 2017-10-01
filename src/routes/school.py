from flask_restplus import Resource, fields
from src.models import School
from src.routes import namespace, api
from src import dbi

school_model = api.model('School', {
  'name': fields.String(),
  'slug': fields.String(),
  'domains': fields.List(fields.String())
})

schools_model = api.model('Schools', {
  'schools': fields.List(fields.Nested(school_model)),
})


@namespace.route('/schools')
class GetSchools(Resource):
  """Fetch all non-destroyed Schools"""

  @namespace.doc('get_schools')
  @namespace.marshal_with(schools_model)
  def get(self):
    schools = dbi.find_all(School)
    school_data = [{'name': s.name, 'slug': s.slug, 'domains': s.domains} for s in schools]
    return {'schools': school_data}