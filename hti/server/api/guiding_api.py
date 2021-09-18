import threading

from flask import request
from flask_restplus import Namespace, Resource

from hti.server.state.globals import (
    get_axis_control,
    get_app_state,
    get_frame_manager,
)
from hti.server.tracking.image_tracker import ImageTracker

api = Namespace('Guiding', description='Guiding API')


@api.route('/guide')
class GuidingApi(Resource):
    @api.doc(
        description='Start guiding',
        response={
            200: 'Success'
        }
    )
    def post(self):
        body = request.json
        device_name = body['device']
        guide_settings = body['settings']

        app_state = get_app_state()
        axis_control = get_axis_control()

        config = {
            "sigma_threshold": 5.0,
            "ra": {
                "enable": guide_settings["raEnable"],
                "range": guide_settings["raRange"],
                "invert": guide_settings["raInvert"],
                "pid_p": guide_settings["raP"],
                "pid_i": guide_settings["raI"],
                "pid_d": guide_settings["raD"]
            },
            "dec": {
                "enable": guide_settings["decEnable"],
                "range": guide_settings["decRange"],
                "invert": guide_settings["decInvert"],
                "pid_p": guide_settings["decP"],
                "pid_i": guide_settings["decI"],
                "pid_d": guide_settings["decD"]
            }
        }

        tracker = ImageTracker(
            config=config,
            device=device_name,
            axis_control=axis_control,
            sample_time=app_state.cameras[device_name].exposure,
            ra_resting_speed_dps=axis_control.speeds.ra_dps,  # use current speeds as defaults
            dec_resting_speed_dps=axis_control.speeds.dec_dps,
        )

        def run_while():
            return app_state.guiding

        frame_manager = get_frame_manager()
        app_state.guiding = True
        threading.Thread(
            target=ImageTracker.run_tracking_loop,
            args=(tracker, frame_manager, run_while),
            daemon=True,
        ).start()
        return '', 200

    @api.doc(
        description='Stop guiding',
        response={
            200: 'Success'
        }
    )
    def delete(self):
        get_app_state().guiding = False
        return '', 200
