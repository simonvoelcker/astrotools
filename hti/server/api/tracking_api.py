import os
import json
import threading
import queue

from flask import request
from flask_restplus import Namespace, Resource

from hti.server.api.events import subscribe_for_events, \
    unsubscribe_from_events, log_event
from hti.server.globals import get_axis_control, get_app_state, \
    get_frame_manager
from lib.image_tracker import ImageTracker
from lib.passive_tracker import PassiveTracker
from lib.target_tracker import TargetTracker

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

        config_file = {
            'target': 'track_target_config.json',
            'image': 'track_image_config.json',
            'passive': 'track_passively_config.json',
        }[mode]

        with open(os.path.join(root_dir, config_file), 'r') as f:
            config = json.load(f)

        tracker_class = {
            'target': TargetTracker,
            'image': ImageTracker,
            'passive': PassiveTracker,
        }[mode]

        axis_control = get_axis_control()
        tracker = tracker_class(
            config,
            axis_control,
            2,  # exposure time of current sequence - TODO!
            axis_control.speeds.ra_dps,  # use current speeds as defaults
            axis_control.speeds.dec_dps,
        )
        if mode == 'target':
            tracker.set_target(get_app_state().target)

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

                def tracking_status_event(message, **kwargs):
                    log_event(f'Tracking status: {message} (Details: {kwargs})')

                tracker.on_new_frame(frame, path_prefix=hti_static_dir, status_change_callback=tracking_status_event)

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
