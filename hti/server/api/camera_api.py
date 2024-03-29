import os
from threading import Thread

from flask import request, send_file
from flask_restplus import Namespace, Resource

from hti.server.state.events import image_event, log_event
from hti.server.state.globals import (
    get_app_state,
    get_camera_controller,
    get_frame_manager,
)
from hti.server.frames_db import FramesDB

api = Namespace('Camera', description='Camera and frame API endpoints')


@api.route('/settings')
class CameraSettingsApi(Resource):
    def put(self):
        """
        Overwrite capturing settings
        """
        body = request.json
        device_name = body['device']

        app_state = get_app_state()
        cam_state = app_state.cameras[device_name]
        cam_state.exposure = float(body['exposure'])
        cam_state.gain = float(body['gain'])
        cam_state.region = body['region']
        cam_state.persist = bool(body['persist'])
        app_state.send_event()


@api.route('/capture')
class CaptureImageApi(Resource):
    def post(self):
        """
        Capture an individual frame
        """
        body = request.json
        device_name = body['device']

        def exp():
            app_state = get_app_state()
            cam_state = app_state.cameras[device_name]
            cam_controller = get_camera_controller()
            frame_manager = get_frame_manager()
            frames_db = FramesDB()
            try:
                cam_state.capturing = True
                app_state.send_event()
                frame = cam_controller.capture_image(device_name, cam_state)
                frame_manager.add_frame(frame, persist=cam_state.persist)
                if cam_state.persist:
                    sequence_id = frames_db.add_sequence(
                        name="Single frame",
                        camera_name=device_name,
                        exposure=cam_state.exposure,
                        gain=cam_state.gain,
                    )
                    frames_db.add_frame(sequence_id, frame.filename)
                cam_state.capturing = False
                app_state.send_event()

                image_event(device_name, frame.path)
                log_event(f'New frame: {frame.path}')

            except TypeError as e:
                log_event(f'Capture error: {e}')
                cam_state.capturing = False
                app_state.send_event()

        Thread(target=exp).start()
        return '', 204


@api.route('/sequence')
class SequenceApi(Resource):
    def post(self):
        """
        Start a capturing sequence
        """
        body = request.json
        device_name = body['device']

        app_state = get_app_state()
        cam_state = app_state.cameras[device_name]

        def run_sequence():
            try:
                cam_controller = get_camera_controller()
                frame_manager = get_frame_manager()
                frames_db = FramesDB()

                if cam_state.persist:
                    sequence_id = frames_db.add_sequence(
                        name="Sequence",
                        camera_name=device_name,
                        exposure=cam_state.exposure,
                        gain=cam_state.gain,
                    )
                else:
                    sequence_id = None

                for frame in cam_controller.capture_sequence(device_name, cam_state):
                    frame_manager.add_frame(frame, persist=cam_state.persist)
                    if cam_state.persist and sequence_id:
                        frames_db.add_frame(sequence_id, frame.filename)
                    image_event(device_name, frame.path)
                    log_event(f'New frame: {frame.path}')

            except Exception as e:
                log_event(f'Capture error: {e}')
            finally:
                cam_state.sequence_stop_requested = False
                cam_state.running_sequence = False
                app_state.send_event()

        cam_state.running_sequence = True
        app_state.send_event()
        Thread(target=run_sequence).start()
        return '', 204

    def delete(self):
        """
        Stop the running sequence
        """
        device_name = request.args.get('device')
        app_state = get_app_state()
        app_state.cameras[device_name].sequence_stop_requested = True
        app_state.send_event()
        return '', 200


@api.route('/frames')
class FrameApi(Resource):
    def get(self):
        """
        Get a frame by its path
        """
        frame_path = request.args.get('framePath')
        if frame_path == 'undefined':
            return 400, 'Bad frame path'

        # Try to find the image in memory
        frame = get_frame_manager().get_frame_by_path(frame_path)
        if frame is None:
            # Send from disk instead
            here = os.path.dirname(os.path.abspath(__file__))
            hti_static_dir = os.path.join(here, '..', 'static')
            path = os.path.normpath(os.path.join(hti_static_dir, frame_path))
            return send_file(path, mimetype='image/png')

        png_data = frame.get_image_data(format='png', for_display=True)
        return send_file(png_data, mimetype='image/png')
