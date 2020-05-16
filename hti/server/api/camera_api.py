import threading

from flask import request
from flask_restplus import Namespace, Resource

from hti.server.api.util import image_event
from hti.server.globals import get_indi_controller, get_app_state

api = Namespace('Control', description='Machine control API endpoints')


@api.route('/<devicename>/capture')
class CaptureImageApi(Resource):
    @api.doc(
        description='Capture an image',
        response={
            200: 'Success'
        }
    )
    def post(self, devicename):
        body = request.json
        exposure = float(body['exposure'])
        gain = float(body['gain'])
        frame_type = body.get('frameType', 'singleCapture')

        def exp():
            controller = get_indi_controller()
            try:
                image_path = controller.capture_image(devicename, frame_type, exposure, gain)
                image_event(image_path)
            except Exception as e:
                print('Capture error:', e)
        threading.Thread(target=exp).start()
        return '', 204


@api.route('/<devicename>/start_sequence')
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
        frame_type = body.get('frameType', 'other')

        def exp():
            try:
                controller = get_indi_controller()
                while get_app_state().get('running_sequence'):
                    image_path = controller.capture_image(devicename, frame_type, exposure, gain)
                    image_event(image_path)
            except Exception as e:
                print('Capture error', e)

        get_app_state()['running_sequence'] = True
        threading.Thread(target=exp).start()
        return '', 204


@api.route('/<devicename>/stop_sequence')
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
