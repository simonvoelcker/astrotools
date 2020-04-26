import queue
import json

from flask import Response
from flask_restplus import Namespace, Resource

from .util import subscribe_for_events


api = Namespace('Info', description='Info API endpoints')


@api.route('/events')
class EventsApi(Resource):
    @api.doc(
        description='Start to get server events',
        response={
            200: 'Success'
        }
    )
    def get(self):
        def gen():
            q = queue.Queue()
            subscribe_for_events(q)
            while True:
                data = q.get()
                yield f'data: {json.dumps(data)}\n\n'
        return Response(gen(), mimetype="text/event-stream")
