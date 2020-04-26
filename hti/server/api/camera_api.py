import os
import threading

from flask import request
from flask.json import jsonify
from flask_restplus import Namespace, Resource

from lib.indi.controller import INDIController
from .util import image_event

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
        here = os.path.dirname(os.path.abspath(__file__))
        workdir = os.path.join(here, '..', '..', 'static', 'images')
        indi_controller = INDIController(workdir)
    return indi_controller


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
            controller = get_indi_controller()
            try:
                image_filename = controller.capture_image(devicename, 'singleCapture', float(exposure), float(gain))
                image_event(image_filename)
            except Exception as e:
                print('Capture error:', e)
        threading.Thread(target=exp).start()
        return '', 204


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
        path_prefix = body['pathPrefix']

        def exp():
            try:
                controller = get_indi_controller()
                while get_app_state().get('running_sequence'):
                    image_filepath = controller.capture_image(devicename, path_prefix, exposure, gain)
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
