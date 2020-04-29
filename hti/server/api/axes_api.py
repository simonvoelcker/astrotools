from flask import request
from flask_restplus import Namespace, Resource

from hti.server.globals import get_axis_control

api = Namespace('Axes', description='Axes control API endpoints')


@api.route('/speed')
class AxesApi(Resource):
    @api.doc(
        description='Set axis speeds',
        response={
            200: 'Success'
        }
    )
    def post(self):
        body = request.json
        ra_speed = float(body['ra'])
        dec_speed = float(body['dec'])

        ra_speed = min(1.0, max(-1.0, ra_speed))
        dec_speed = min(1.0, max(-1.0, dec_speed))

        axis_control = get_axis_control()
        if not axis_control.connected():
            return 'Not connected to motors', 503

        axis_control.set_motor_speed('A', ra_speed)
        axis_control.set_motor_speed('B', dec_speed)
        return '', 200
