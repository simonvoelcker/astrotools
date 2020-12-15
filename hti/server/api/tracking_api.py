import os
import threading
import queue

from flask import request
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
    get_error_recorder,
)
from hti.server.tracking import create_tracker

api = Namespace('Tracking', description='Tracking API')


@api.route('/start')
class TrackTargetApi(Resource):
    @api.doc(
        description='Start tracking with given mode. Target, if required, is assumed to be set beforehand.',
        response={
            200: 'Success'
        }
    )
    def post(self):
        mode = request.json['mode']

        here = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.normpath(os.path.join(here, '..', '..', '..'))

        axis_control = get_axis_control()
        # TODO: frame cadence is hardcoded here.
        # move exposure time to BE state, use that
        tracker = create_tracker(mode, 2, axis_control)

        if mode == 'target':
            tracker.set_target(get_app_state().target)

        if mode == 'passive':
            tracker.set_error_recorder(get_error_recorder())

        def thread_func():
            # process most recent events first and discard old ones
            q = queue.LifoQueue()
            subscribe_for_events(q)
            latest_processed_event = None
            frame_manager = get_frame_manager()
            while get_app_state().tracking:
                event = q.get()
                if event['type'] != 'image':
                    continue
                if latest_processed_event and latest_processed_event['unix_timestamp'] >= event['unix_timestamp']:
                    # skip over old events
                    continue
                latest_processed_event = event
                frame_path = event['image_path']
                frame = frame_manager.get_frame_by_path(frame_path)
                hti_static_dir = os.path.join(root_dir, 'hti', 'static')

                tracker.on_new_frame(frame, path_prefix=hti_static_dir)

            log_event(f'Tracking status: Stopped')
            unsubscribe_from_events(q)

        get_app_state().tracking = True
        threading.Thread(target=thread_func, daemon=True).start()
        return '', 200


@api.route('/stop')
class StopTrackingApi(Resource):
    @api.doc(
        description='Stop tracking',
        response={
            200: 'Success'
        }
    )
    def post(self):

        # TODO killing the thread would have the advantage that
        # does it does not block indefinitely if capturing was stopped
        # and it would ensure there cannot be two tracking threads, ever

        get_app_state().tracking = False
        return '', 200
