import time

from threading import Thread
from flask import request
from flask_restplus import Namespace, Resource

from hti.server.state.globals import get_axis_control, get_app_state

api = Namespace('Axes', description='Axes control API endpoints')


@api.route('/speeds')
class SetSpeedApi(Resource):
    @api.doc(
        description='Set axis speeds, in degrees per second',
        response={
            200: 'Success'
        }
    )
    def post(self):
        body = request.json
        ra_speed = float(body['ra'])
        dec_speed = float(body['dec'])

        # abort any steering maneuver
        app_state = get_app_state()
        if app_state.steering:
            app_state.steering = False
            time.sleep(1)

        axis_control = get_axis_control()
        mode = 'manual' if ra_speed or dec_speed else 'stopped'
        axis_control.set_axis_speeds(ra_dps=ra_speed, dec_dps=dec_speed, mode=mode)
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
        # abort any steering maneuver
        app_state = get_app_state()
        if app_state.steering:
            app_state.steering = False
            time.sleep(1)

        get_axis_control().set_resting()
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
        axis_control = get_axis_control()

        def steer_fun():
            app_state.steering = True
            axis_control.steer(
                app_state.last_known_position['position'],
                app_state.target,
                max_speed_dps=1.0,
                run_callback=lambda: app_state.steering
            )
            app_state.steering = False

        Thread(target=steer_fun).start()
        return '', 200
