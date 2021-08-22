from threading import Thread

from flask import request, send_file
from flask_restplus import Namespace, Resource

from hti.server.state.events import image_event, log_event
from hti.server.state.globals import (
    get_app_state,
    get_camera_controller,
    get_frame_manager,
    CameraState,
)
from hti.server.utils import pick_guiding_region

api = Namespace('Camera', description='Camera and frame API endpoints')


@api.route('/settings')
class CameraSettingsApi(Resource):
    @api.doc(
        description='Capture an image',
        response={
            200: 'Success'
        }
    )
    def post(self):
        body = request.json
        device_name = body['device']

        app_state = get_app_state()
        app_state.cameras[device_name] = CameraState(
            exposure=float(body['exposure']),
            gain=float(body['gain']),
            capturing=app_state.cameras[device_name].capturing,
            running_sequence=app_state.cameras[device_name].running_sequence,
            persist=bool(body['persist']),
            frame_type=body['frameType'],
        )


@api.route('/capture')
class CaptureImageApi(Resource):
    @api.doc(
        description='Capture an image',
        response={
            200: 'Success'
        }
    )
    def post(self):
        body = request.json
        device_name = body['device']

        def exp():
            cam_state = get_app_state().cameras[device_name]
            cam_controller = get_camera_controller()
            frame_manager = get_frame_manager()
            try:
                cam_state.capturing = True
                frame = cam_controller.capture_image(
                    device_name,
                    frame_type=cam_state.frame_type,
                    exposure=cam_state.exposure,
                    gain=cam_state.gain,
                )
                frame_manager.add_frame(
                    frame,
                    persist=cam_state.persist,
                )
                cam_state.capturing = False

                image_event(frame.path)
                log_event(f'New frame: {frame.path}')

            except TypeError as e:
                log_event(f'Capture error: {e}')
                cam_state.capturing = False

        Thread(target=exp).start()
        return '', 204


@api.route('/sequence')
class SequenceApi(Resource):
    @api.doc(
        description='Start sequence',
        response={
            200: 'Success'
        }
    ) 
    def post(self):
        body = request.json
        device_name = body['device']

        def exp():
            try:
                cam_state = get_app_state().cameras[device_name]
                cam_controller = get_camera_controller()
                frame_manager = get_frame_manager()

                def run_while():
                    return cam_state.running_sequence

                for frame in cam_controller.capture_sequence(
                    device_name,
                    frame_type=cam_state.frame_type,
                    exposure=cam_state.exposure,
                    gain=cam_state.gain,
                    run_while=run_while(),
                ):
                    frame_manager.add_frame(frame, persist=cam_state.persist)
                    image_event(frame.path)
                    log_event(f'New frame: {frame.path}')

            except Exception as e:
                log_event(f'Capture error: {e}')

        get_app_state().cameras[device_name].running_sequence = True
        Thread(target=exp).start()
        return '', 204

    @api.doc(
        description='Stop sequence',
        response={
            200: 'Success'
        }
    ) 
    def delete(self):
        body = request.json
        device_name = body['device']
        get_app_state().cameras[device_name].running_sequence = False
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
        frame_path = request.args.get('framePath')
        frame = get_frame_manager().get_frame_by_path(frame_path)
        if frame is None:
            return '', 404

        png_data = frame.get_image_data(format='png', for_display=True)
        return send_file(png_data, mimetype='image/png')


@api.route('/autoguide')
class StartGuidingApi(Resource):
    @api.doc(
        description='Start auto-guiding',
        response={
            200: 'Success'
        }
    )
    def post(self):
        # TODO guiding must be full auto in the future
        # exposure time must be low, gain determined via bisecting
        body = request.json
        exposure = float(body['exposure'])
        gain = float(body['gain'])

        app_state = get_app_state()
        cam_controller = get_camera_controller()

        app_state.capturing = True
        frame = cam_controller.capture_image('guiding', exposure, gain)
        app_state.capturing = False

        region_radius = 100
        guiding_region = pick_guiding_region(frame, radius=100)

        # TODO this is incomplete

        return '', 204

    @api.doc(
        description='Stop auto-guiding',
        response={
            200: 'Success'
        }
    )
    def delete(self):
        return '', 200
