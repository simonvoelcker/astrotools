from flask_restplus import Namespace, Resource

api = Namespace('Axes', description='Axes control API endpoints')


@api.route('/<axis>/speed')
class AxesApi(Resource):
    @api.doc(
        description='Get axis speed',
        response={
            200: 'Success'
        }
    )
    def get(self, axis):
        return '', 200
