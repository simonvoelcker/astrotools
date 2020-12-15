import threading
import queue

from flask_restplus import Namespace, Resource

from hti.server.state.events import (
    subscribe_for_events,
    unsubscribe_from_events,
    log_event,
)
from hti.server.state.globals import (
    get_axis_control,
    get_app_state,
    get_frame_manager,
)
from hti.server.tracking import create_tracker

api = Namespace('Guiding', description='Guiding API')


def run_tracking_loop(tracker, run_callback):

    # process most recent events first and discard old ones
    q = queue.LifoQueue()
    subscribe_for_events(q)
    latest_processed_event = None
    frame_manager = get_frame_manager()

    while run_callback():
        event = q.get()
        if event['type'] != 'image':
            continue
        if latest_processed_event and latest_processed_event['unix_timestamp'] >= event['unix_timestamp']:
            # skip over old events
            continue
        latest_processed_event = event
        frame_path = event['image_path']
        frame = frame_manager.get_frame_by_path(frame_path)
        tracker.on_new_frame(frame)

    log_event(f'Tracking status: Stopped')
    unsubscribe_from_events(q)


@api.route('/start')
class TrackGuidingApi(Resource):
    @api.doc(
        description='Start guiding',
        response={
            200: 'Success'
        }
    )
    def post(self):

        # TODO: frame cadence is hardcoded here.
        # move exposure time to BE state, use that
        tracker = create_tracker('image', 2, get_axis_control())

        # if mode == 'passive':
        #     tracker.set_error_recorder(get_error_recorder())

        def run_while():
            return get_app_state().guiding

        get_app_state().guiding = True
        threading.Thread(
            target=run_tracking_loop,
            args=(tracker, run_while),
            daemon=True,
        ).start()
        return '', 200


@api.route('/stop')
class StopGuidingApi(Resource):
    @api.doc(
        description='Stop guiding',
        response={
            200: 'Success'
        }
    )
    def post(self):
        get_app_state().guiding = False
        return '', 200
