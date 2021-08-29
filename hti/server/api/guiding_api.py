import threading

from flask import request
from flask_restplus import Namespace, Resource

from hti.server.state.globals import (
    get_axis_control,
    get_app_state,
    get_frame_manager, get_pec_manager,
)
from hti.server.tracking import create_tracker, Tracker

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

        # 3 options:
        # 1) use full frame for guiding
        # 2) select ROI manually in FE
        # 3) detect ROI automatically

        # 2 options for detecting offsets:
        # 1) register_translation
        # 2) image2xy in a subprocess

        # 2 major todos: select ROI UI, image2xy integration

        app_state = get_app_state()
        tracker = create_tracker(
            'image',
            device_name,
            app_state.cameras[device_name].exposure,
            get_axis_control(),
            get_pec_manager(),
        )

        def run_while():
            return app_state.guiding

        frame_manager = get_frame_manager()
        app_state.guiding = True
        threading.Thread(
            target=Tracker.run_tracking_loop,
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
