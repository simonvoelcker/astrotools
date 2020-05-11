import queue
import json
import os

from flask import Response, request
from flask_restplus import Namespace, Resource
from flask.json import jsonify

from hti.server.api.util import subscribe_for_events
from hti.server.globals import get_catalog, get_app_state

from lib.coordinates import Coordinates
from lib.solver import Solver

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
            target = {
                'ra': parsed_coordinates.ra,
                'dec': parsed_coordinates.dec
            }
            get_app_state()['target'] = target
            return jsonify(target)

        catalog_result = get_catalog().get_entry(query.upper())
        if catalog_result is not None:
            parsed_coordinates = Coordinates.parse_csvformat(catalog_result['RA'], catalog_result['Dec'])
            target = {
                'name': catalog_result['Name'],
                'ra': parsed_coordinates.ra,
                'dec': parsed_coordinates.dec,
                'type': catalog_result.get('Type'),
                'const': catalog_result.get('Const'),
                'minAx': catalog_result.get('MinAx'),
                'majAx': catalog_result.get('MajAx'),
                'posAng': catalog_result.get('PosAng'),
            }
            get_app_state()['target'] = target
            return jsonify(target)

        return '', 404


@api.route('/images/calibrate')
class CalibrateImageApi(Resource):
    @api.doc(
        description='Get calibration data of given image',
        response={
            200: 'Success',
            404: 'Image not found or failed to calibrate'
        }
    )
    def post(self):
        body = request.json
        image_path = body['imagePath']
        timeout = float(body['timeout'])

        here = os.path.dirname(os.path.abspath(__file__))
        hti_static_dir = os.path.join(here, '..', '..', 'static')
        image_path = os.path.join(hti_static_dir, image_path)

        if not os.path.isfile(image_path):
            return 'Image not found', 404

        calibration_data = Solver().analyze_image(image_path, timeout)
        if calibration_data is None:
            return 'Failed to calibrate', 404

        center = calibration_data['center_deg']
        get_app_state()['here'] = Coordinates(float(center['ra']), float(center['dec']))

        return jsonify(calibration_data)
