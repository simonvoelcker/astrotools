import os
import json
import threading
import queue

from flask import request
from flask_restplus import Namespace, Resource

from hti.server.api.events import subscribe_for_events, unsubscribe_from_events
from hti.server.globals import get_axis_control, get_app_state
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

        tracker = None
        if mode == 'target':
            axis_control = get_axis_control()
            tracker = TargetTracker(config, axis_control)
            tracker.set_target(get_app_state().target)
        elif mode == 'image':
            axis_control = get_axis_control()
            tracker = ImageTracker(config, axis_control)
        elif mode == 'passive':
            tracker = PassiveTracker(config)

        def thread_func():
            # process most recent events first and discard old ones
            q = queue.LifoQueue()
            subscribe_for_events(q)
            latest_processed_event = None
            while get_app_state().tracking:
                event = q.get()
                if event['type'] != 'image':
                    continue
                if latest_processed_event and latest_processed_event['unix_timestamp'] >= event['unix_timestamp']:
                    # skip over old events
                    continue
                latest_processed_event = event
                image_path = event['image_path']  # relative to static
                absolute_image_path = os.path.join(root_dir, 'hti', 'static', image_path)

                def tracking_status_event(message, **kwargs):
                    get_app_state().tracking_status = {
                        'message': message,
                        'details': kwargs,
                    }

                tracker.on_new_file(absolute_image_path, status_change_callback=tracking_status_event)

            # TODO this must also happen on exception
            get_app_state().tracking_status = {
                'message': 'Stopped',
                'details': None
            }
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
