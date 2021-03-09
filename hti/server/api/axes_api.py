import time
import numpy as np

from threading import Thread
from flask import request
from flask_restplus import Namespace, Resource

from hti.server.state.globals import (
    get_axis_control,
    get_app_state,
    get_camera_controller,
)
from lib.frame_quality_analyzer import FrameQualityAnalyzer

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


@api.route('/focus')
class FocusApi(Resource):
    @api.doc(
        description='Move focus axis by given number of steps',
        response={
            200: 'Success'
        }
    )
    def post(self):
        body = request.json
        steps = int(body['steps'])
        get_axis_control().move_focus_axis(steps)
        return '', 200


@api.route('/auto-focus')
class FocusApi(Resource):

    def determine_hfd(self, num_samples):
        cam_controller = get_camera_controller()
        samples = []
        for _ in range(num_samples):
            frame = cam_controller.capture_image('focus', 1.0, 20000)
            numpy_image = frame.get_numpy_image()
            image_greyscale = np.average(numpy_image, axis=2)
            sample = FrameQualityAnalyzer().compute_hfd(image_greyscale)
            samples.append(sample)
        return sum(samples) / num_samples

    def run_focus_sequence(self, increment, num_samples):
        last_hfd = self.determine_hfd(num_samples)
        while True:
            self.move_focus(increment)
            new_hfd = self.determine_hfd(num_samples)
            if new_hfd > last_hfd:
                print(f'HFD {new_hfd:.3f} => Done')
                return
            else:
                print(f'HFD {new_hfd:.3f}')
            last_hfd = new_hfd

    def move_focus(self, increment):
        print(f'Moving focus by {increment}')
        axis_control = get_axis_control()
        axis_control.move_focus_axis(increment)
        time.sleep(abs(increment) / 100.0)

    @api.doc(
        description='Run the auto-focus sequence',
        response={
            200: 'Success',
            400: 'Bad request',
        }
    )
    def post(self):
        app_state = get_app_state()
        if app_state.capturing or app_state.running_sequence:
            return 'Cannot do this while capturing', 400

        app_state.running_sequence = True

        print('Running auto-focus')
        hfd = self.determine_hfd(num_samples=10)
        print(f'HFD at start: {hfd}')

        self.move_focus(-700)
        self.move_focus(+200)

        hfd = self.determine_hfd(num_samples=10)
        print(f'HFD now: {hfd}')

        self.run_focus_sequence(increment=100, num_samples=10)

        self.move_focus(-300)
        self.move_focus(200)

        hfd = self.determine_hfd(num_samples=10)
        print(f'HFD now: {hfd}')

        self.run_focus_sequence(increment=25, num_samples=10)

        hfd = self.determine_hfd(num_samples=10)
        print(f'HFD in the end: {hfd}')

        print('All done')
        app_state.running_sequence = False
        return '', 200
