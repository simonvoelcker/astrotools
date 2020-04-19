import os
import queue
import threading
import json

from flask import Flask, render_template, request, Response
from flask import current_app as app
from flask.json import jsonify
from flask_restplus import Namespace, Resource

from server.lib.indi.controller import INDIController
from .util import subscribe_for_events, image_event

api = Namespace('Control', description='Machine control API endpoints')


app_state = None
indi_controller = None


def get_app_state():
    global app_state
    if app_state is None:
        app_state = dict()
    return app_state


def get_indi_controller():
    global indi_controller
    if indi_controller is None:
        with app.app_context():
            # TODO could try a relative path here, or abspath
            indi_controller = INDIController(workdir=os.path.join(app.static_folder, 'images'))
    return indi_controller


@api.route('/status')
class StatusApi(Resource):
    @api.doc(
        description='Get controller status',
        response={
            200: 'Success'
        }
    )
    def get(self):
        return jsonify(get_indi_controller().status())

@api.route('/clean-cache')
class CleanCacheApi(Resource):
    @api.doc(
        description='Clean the INDI cache',
        response={
            200: 'Success'
        }
    )
    def get(self):
        numfiles = get_indi_controller().clean_cache()
        return jsonify({'files': numfiles})

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

@api.route('/devices')
class DevicesApi(Resource):
    @api.doc(
        description='List devices',
        response={
            200: 'Success'
        }
    )
    def get(self):
        return jsonify(get_indi_controller().devices())

@api.route('/device_names')
class DeviceNamesApi(Resource):
    @api.doc(
        description='List device names',
        response={
            200: 'Success'
        }
    )
    def get(self):
        return jsonify({'devices': get_indi_controller().device_names()})

@api.route('/device/<devicename>/properties')
class DevicePropertiesListApi(Resource):
    @api.doc(
        description='List device properties',
        response={
            200: 'Success'
        }
    )
    def get(self, devicename):
        return jsonify(get_indi_controller().properties(devicename))

@api.route('/device/<devicename>/properties/<property>')
class DevicePropertyApi(Resource):
    @api.doc(
        description='Get device property',
        response={
            200: 'Success'
        }
    )
    def get(self, devicename, property):
        return jsonify(get_indi_controller().property(devicename, property))

    @api.doc(
        description='Set device property',
        response={
            200: 'Success'
        }
    )
    def put(self, devicename, property):
        return jsonify(get_indi_controller().set_property(devicename, property, request.json['value']))

@api.route('/device/<devicename>/capture/<exposure>/<gain>')
class CaptureImageApi(Resource):
    @api.doc(
        description='Capture an image',
        response={
            200: 'Success'
        }
    )
    def get(self, devicename, exposure, gain):
        def exp():
            try:
                image_event(get_indi_controller().capture_image(devicename, float(exposure), float(gain)))
            except Exception as e:
                print('Capture error', e)
        threading.Thread(target=exp).start()
        return ('', 204)

@api.route('/device/<devicename>/start_sequence')
class StartSequenceApi(Resource):
    @api.doc(
        description='Start image sequence',
        response={
            200: 'Success'
        }
    ) 
    def post(self, devicename):
        body = request.json
        exposure = float(body['exposure'])
        gain = float(body['gain'])
        pathprefix = body['pathprefix']

        def exp():
            try:
                controller = get_indi_controller()
                while get_app_state().get('running_sequence'):
                    image_filepath = controller.capture_image(devicename, exposure, gain) 
                    image_event(image_filepath)
            except Exception as e:
                print('Capture error', e)

        get_app_state()['running_sequence'] = True
        threading.Thread(target=exp).start()
        return '', 204

@api.route('/device/<devicename>/stop_sequence')
class StopSequenceApi(Resource):
    @api.doc(
        description='Start image sequence',
        response={
            200: 'Success'
        }
    ) 
    def get(self, devicename):
        get_app_state()['running_sequence'] = False
        return '', 200
