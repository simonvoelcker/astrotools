import os
import json
import threading
import queue

from flask import request
from flask_restplus import Namespace, Resource

from hti.server.api.util import subscribe_for_events, unsubscribe_from_events
from hti.server.globals import get_axis_control, get_app_state
from lib.coordinates import Coordinates
from lib.target_tracker import TargetTracker

api = Namespace('Tracking', description='Tracking API')


@api.route('/startWithTarget')
class TrackTargetApi(Resource):
    @api.doc(
        description='Track the given target continuously',
        response={
            200: 'Success'
        }
    )
    def post(self):
        body = request.json
        target = Coordinates(float(body['target']['ra']), float(body['target']['dec']))

        here = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.join(here, '..', '..', '..')
        config_file = os.path.join(root_dir, 'track_target_config.json')
        with open(config_file, 'r') as f:
            config = json.load(f)

        axis_control = get_axis_control()
        tracker = TargetTracker(config, axis_control)
        tracker.set_target(target)

        def thread_func():
            q = queue.Queue()
            subscribe_for_events(q)
            while get_app_state()['tracking']:
                # TODO the queue can be full of shit after a long steering maneuver
                event = q.get()
                if event['type'] == 'image':
                    image_path = event['image_path']  # relative to static
                    absolute_image_path = os.path.join(root_dir, 'hti', 'static', image_path)
                    tracker.on_new_file(absolute_image_path)
            # TODO this must also happen on exception
            unsubscribe_from_events(q)

        get_app_state()['tracking'] = True
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
        get_app_state()['tracking'] = False
        return '', 200
