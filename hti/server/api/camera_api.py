from threading import Thread

from flask import request, send_file
from flask_restplus import Namespace, Resource

from hti.server.api.events import image_event, log_event
from hti.server.globals import (
    get_app_state,
    get_camera_controller,
    get_frame_manager,
)
from lib.image_tracker import ImageTracker

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
        persist = bool(body['persist'])
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
                frame_manager.add_frame(frame, persist)
                app_state.capturing = False
                image_event(frame.path)
                log_event(f'New frame: {frame.path}')

                guiding_region = ImageTracker.pick_guiding_region(
                    frame, radius=100
                )
                app_state.annotations = [guiding_region]

            except Exception as e:
                log_event(f'Capture error: {e}')
                app_state.capturing = False

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
        persist = bool(body['persist'])
        frame_type = body.get('frameType', 'other')

        def exp():
            try:
                app_state = get_app_state()
                cam_controller = get_camera_controller()
                frame_manager = get_frame_manager()

                for frame in cam_controller.capture_sequence(
                    devicename,
                    frame_type,
                    exposure,
                    gain,
                    run_callback=lambda: app_state.running_sequence,
                ):
                    frame_manager.add_frame(frame, persist)
                    image_event(frame.path)
                    log_event(f'New frame: {frame.path}')
            except Exception as e:
                log_event(f'Capture error: {e}')

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
        frame_path = request.args.get('framePath')
        frame = get_frame_manager().get_frame_by_path(frame_path)
        if frame is None:
            return '', 404

        png_data = frame.get_image_data(format='png', downscale=2)
        return send_file(png_data, mimetype='image/png')


@api.route('/<devicename>/autoguide')
class StartGuidingApi(Resource):
    @api.doc(
        description='Start auto-guiding',
        response={
            200: 'Success'
        }
    )
    def post(self, devicename):
        # TODO guiding must be full auto in the future
        # exposure time must be low, gain determined via bisecting
        body = request.json
        exposure = float(body['exposure'])
        gain = float(body['gain'])

        app_state = get_app_state()
        cam_controller = get_camera_controller()

        app_state.capturing = True
        frame = cam_controller.capture_image(
            devicename, 'guiding', exposure, gain
        )
        app_state.capturing = False

        region_radius = 100
        guiding_region = ImageTracker.pick_guiding_region(frame, region_radius)
        # TODO test region by sending this off to FE and display, will be cool
        # to make it easier to test, use latest frame instead of capturing one

        return '', 204

    @api.doc(
        description='Stop auto-guiding',
        response={
            200: 'Success'
        }
    )
    def delete(self, devicename):
        return '', 200