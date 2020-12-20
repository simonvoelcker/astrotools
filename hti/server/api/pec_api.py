import threading

from flask_restplus import Namespace, Resource
from flask import request

from hti.server.tracking.tracker import Tracker
from hti.server.state.globals import (
    get_axis_control,
    get_app_state,
    get_pec_manager,
    get_frame_manager,
)
from hti.server.tracking import create_tracker

api = Namespace('PEC', description='Periodic Error Compensation API')


@api.route('/record')
class RecordPeriodicError(Resource):
    @api.doc(
        description='Start recording periodic error',
        response={
            200: 'Success'
        }
    )
    def post(self):
        app_state = get_app_state()
        tracker = create_tracker(
            'passive',
            app_state.capture_state.exposure,
            get_axis_control(),
            get_pec_manager(),
        )

        def run_while():
            return app_state.pec_state.recording

        frame_manager = get_frame_manager()
        app_state.pec_state.recording = True
        threading.Thread(
            target=Tracker.run_tracking_loop,
            args=(tracker, frame_manager, run_while),
            daemon=True,
        ).start()
        return '', 200

    @api.doc(
        description='Stop recording periodic error',
        response={
            200: 'Success'
        }
    )
    def delete(self):
        get_app_state().pec_state.recording = False
        return '', 200


@api.route('/replay')
class ReplayPeriodicError(Resource):
    @api.doc(
        description='Start replaying periodic error',
        response={
            200: 'Success'
        }
    )
    def post(self):
        app_state = get_app_state()
        tracker = create_tracker(
            'passive',
            app_state.capture_state.exposure,
            get_axis_control(),
            get_pec_manager(),
        )

        def run_while():
            return app_state.pec_state.replaying

        frame_manager = get_frame_manager()
        app_state.pec_state.replaying = True
        threading.Thread(
            target=Tracker.run_tracking_loop,
            args=(tracker, frame_manager, run_while),
            daemon=True,
        ).start()
        return '', 200

    @api.doc(
        description='Stop replaying periodic error',
        response={
            200: 'Success'
        }
    )
    def delete(self):
        get_app_state().pec_state.replaying = False
        return '', 200


@api.route('/set-factor')
class SetPECFactor(Resource):
    @api.doc(
        description='Set the speed factor used in PEC',
        response={
            200: 'Success'
        }
    )
    def post(self):
        body = request.json
        factor = float(body['factor'])
        get_app_state().pec_state.factor = factor
        get_app_state().send_event()
