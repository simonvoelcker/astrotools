from threading import Thread

from flask import request, send_file
from flask_restplus import Namespace, Resource

from hti.server.api.events import image_event, log_event
from hti.server.globals import (
    get_app_state,
    get_camera_controller,
    get_frame_manager,
)

api = Namespace('Camera', description='Camera and frame API endpoints')


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
            app_state = get_app_state()
            cam_controller = get_camera_controller()
            frame_manager = get_frame_manager()
            try:
                app_state.capturing = True
                frame = cam_controller.capture_image(
                    devicename, frame_type, exposure, gain
                )
                frame_manager.add_frame(frame)
                app_state.capturing = False
                image_event(frame.path)
                log_event(f'New frame: {frame.path}')
            except Exception as e:
                print('Capture error:', e)

        Thread(target=exp).start()
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
                cam_controller = get_camera_controller()
                frame_manager = get_frame_manager()
                while get_app_state().running_sequence:
                    frame = cam_controller.capture_image(
                        devicename, frame_type, exposure, gain
                    )
                    frame_manager.add_frame(frame)
                    image_event(frame.path)
                    log_event(f'New frame: {frame.path}')
            except Exception as e:
                print('Capture error', e)

        get_app_state().running_sequence = True
        Thread(target=exp).start()
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
        get_app_state().running_sequence = False
        return '', 200


@api.route('/frames')
class FrameApi(Resource):
    @api.doc(
        description='Get a frame by its path (URL parameter)',
        response={
            200: 'Success'
        }
    )
    def get(self):
        image_path = request.args.get('imagePath')
        frame = get_frame_manager().get_frame_by_path(image_path)
        if frame is None:
            return '', 404

        png_data = frame.get_image_data(format='png')
        return send_file(png_data, mimetype='image/png')
