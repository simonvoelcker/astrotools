import queue
import json

from flask import Response
from flask_restplus import Namespace, Resource
from flask.json import jsonify

from hti.server.api.util import subscribe_for_events
from hti.server.globals import get_catalog

from lib.coordinates import Coordinates

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


@api.route('/target/<query>')
class QueryTargetApi(Resource):
    @api.doc(
        description='Get coordinates from target description',
        response={
            200: 'Success',
            404: 'Object not found in catalog'
        }
    )
    def get(self, query):

        parsed_coordinates = Coordinates.parse(query)
        if parsed_coordinates is not None:
            return jsonify({
                'name': '(custom)',
                'ra': parsed_coordinates.ra,
                'dec': parsed_coordinates.dec
            })

        catalog_result = get_catalog().get_entry(query.upper())
        if catalog_result is not None:
            parsed_coordinates = Coordinates.parse_csvformat(catalog_result['RA'], catalog_result['Dec'])
            return jsonify({
                'name': catalog_result['Name'],
                'ra': parsed_coordinates.ra,
                'dec': parsed_coordinates.dec
            })

        return '', 404
