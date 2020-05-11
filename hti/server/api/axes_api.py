from flask import request
from flask_restplus import Namespace, Resource

from hti.server.globals import get_axis_control, get_app_state
from lib.axis_control import AxisControl
from lib.coordinates import Coordinates

api = Namespace('Axes', description='Axes control API endpoints')


@api.route('/speeds')
class SetSpeedApi(Resource):
    @api.doc(
        description='Get axis speeds',
        response={
            200: 'Success'
        }
    )
    def get(self):
        return get_axis_control().get_speeds()

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
        axis_control.set_motor_speed('A', ra_speed)
        axis_control.set_motor_speed('B', dec_speed)
        return '', 200


# RestApi! Get it? Heh.
@api.route('/rest')
class RestApi(Resource):
    @api.doc(
        description='Set axes to resting speed',
        response={
            200: 'Success'
        }
    )
    def post(self):
        axis_control = get_axis_control()
        axis_control.set_motor_speed('A', AxisControl.ra_resting_speed)
        axis_control.set_motor_speed('B', AxisControl.dec_resting_speed)
        return '', 200


@api.route('/gototarget')
class GoToApi(Resource):
    @api.doc(
        description='Steer to target. Assumes last known position and target set',
        response={
            200: 'Success'
        }
    )
    def post(self):
        app_state = get_app_state()
        here = app_state['here']
        target = app_state['target']
        # TODO this is grütze
        target = Coordinates(float(target['ra']), float(target['dec']))

        axis_control = get_axis_control()
        # TODO this will block. need app state "steering" or so. should also be stoppable.
        axis_control.steer(here, target, max_speed_dps=1.0)
        return '', 200

