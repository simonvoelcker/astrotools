import threading

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
        # TODO: frame cadence is hardcoded here.
        # move exposure time to BE state, use that
        tracker = create_tracker(
            'image', 2, get_axis_control(), get_pec_manager(),
        )

        def run_while():
            return get_app_state().guiding

        frame_manager = get_frame_manager()
        get_app_state().guiding = True
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
