import queue
import json
import os
import datetime

from threading import Thread

from flask import Response, request
from flask_restplus import Namespace, Resource
from flask.json import jsonify

from hti.server.state.events import subscribe_for_events, log_event
from hti.server.state.globals import (
    get_catalog,
    get_app_state,
    get_frame_manager,
)

from .util import camel_case_keys_recursively, to_dict_recursively

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
            # Send an event with the current app state
            get_app_state().send_event()
            while True:
                data = q.get()
                # convert objects to dicts and make keys camel case
                data_dict = to_dict_recursively(data)
                camel_case_dict = camel_case_keys_recursively(data_dict)
                yield f'data: {json.dumps(camel_case_dict)}\n\n'
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
            get_app_state().target = parsed_coordinates
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
            get_app_state().target = parsed_coordinates
            return jsonify(target)

        return '', 404


@api.route('/stars')
class QueryStarsApi(Resource):
    @api.doc(
        description='Get a list of stars based on query criteria',
        response={
            200: 'Success',
        }
    )
    def get(self):
        count = request.args.get('count') if 'count' in request.args else 1000
        area = {
            'raMin': request.args.get('raMin'),
            'raMax': request.args.get('raMax'),
            'decMin': request.args.get('decMin'),
            'decMax': request.args.get('decMax'),
        } if 'raMin' in request.args else None
        stars = get_catalog().get_stars(area=area, count=count)
        return stars, 200


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
        frame_path = body['framePath']
        timeout = float(body['timeout'])

        frame = get_frame_manager().get_frame_by_path(frame_path)
        if frame is None:
            return 'Frame not found', 404

        here = os.path.dirname(os.path.abspath(__file__))
        hti_static_dir = os.path.join(here, '..', '..', 'static')

        if not frame.persisted:
            frame.persist(hti_static_dir)

        filepath = os.path.join(hti_static_dir, frame.path)

        app_state = get_app_state()

        def analyze_fun():
            app_state.calibrating = True
            calibration_data = Solver().analyze_image(
                filepath,
                timeout,
                run_callback=lambda: app_state.calibrating,
            )
            app_state.calibrating = False

            timestamp = int(datetime.datetime.now().timestamp())

            if calibration_data is None:
                log_event('Calibration failed')
            else:
                rotation_angle = calibration_data.rotation_angle
                position = calibration_data.center_deg

                log_event(f'Image center: {position} Rotation: {rotation_angle}')

                if app_state.target is not None:
                    target_distance = Coordinates(
                        app_state.target.ra - position.ra,
                        app_state.target.dec - position.dec
                    )
                    log_event(f'Distance to target: {target_distance}')

                app_state.last_known_position = {
                    'timestamp': timestamp,
                    'position': position,
                }

        Thread(target=analyze_fun).start()
        return '', 200


@api.route('/images/calibrate/stop')
class CalibrateImageApi(Resource):
    @api.doc(
        description='Stop running calibration',
        response={
            200: 'Success',
        }
    )
    def post(self):
        get_app_state().calibrating = False
        return '', 200


@api.route('/directory')
class ListDirectoryApi(Resource):

    def _list_dir_recursively(self, path: str) -> list:
        entries = list(os.listdir(path))
        entries.sort()
        for entry_index, entry in enumerate(entries):
            sub_path = os.path.join(path, entry)
            if os.path.isdir(sub_path):
                entries[entry_index] = {
                    'name': entry,
                    'children': self._list_dir_recursively(sub_path)
                }
        return entries

    @api.doc(
        description='List subdirectories and files of given directory',
        response={
            200: 'Success',
            400: 'Malformed request',
            404: 'Directory not found'
        }
    )
    def post(self):
        body = request.json
        if body is None:
            return 'Missing request body', 400
        path = body.get('path')  # path is understood to be relative to static
        recursive = body.get('recursive', False)
        if path is None:
            return 'Missing path in request body', 400

        here = os.path.dirname(os.path.abspath(__file__))
        hti_static_dir = os.path.join(here, '..', '..', 'static')
        final_path = os.path.normpath(os.path.join(hti_static_dir, path))
        if not os.path.isdir(final_path):
            return f'Directory {final_path} not found', 404

        if recursive:
            entries = self._list_dir_recursively(final_path)
        else:
            entries = os.listdir(final_path)
            entries.sort()
        return jsonify(entries)
