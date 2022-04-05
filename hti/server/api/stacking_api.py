from flask_restplus import Namespace, Resource
from flask import request, send_file

from hti.server.api.util import find_frame_path
from hti.server.frames_db import FramesDB
from hti.server.state.globals import get_image_stacker, get_app_state

from lib.frame import Frame
from lib.solver import CalibrationData
from lib.coordinates import Coordinates

api = Namespace('Stacking', description='Stacking API endpoints')


@api.route('/stack')
class StackingApi(Resource):
    @api.doc(
        description='Stack images',
        response={200: 'Success'},
    )
    def post(self):
        frames_db = FramesDB()

        body = request.json
        lights_sequence_id = int(body['lightsSequenceId'])

        light_frames = frames_db.list_analyzed_frames(lights_sequence_id)

        frames = []
        for frame_info in light_frames:
            frame_path = find_frame_path(frame_info["filename"])
            if not frame_path:
                print("Skipped a frame not found on disk")
                continue

            calibration_data = CalibrationData(
                pixel_scale=frame_info["pixel_scale"],
                pixel_scale_unit=frame_info["pixel_scale_unit"],
                center_deg=Coordinates(
                    frame_info["center_ra"],
                    frame_info["center_dec"],
                ),
                rotation_angle=frame_info["rotation_angle"],
                rotation_direction=frame_info["rotation_direction"],
                parity=frame_info["parity"],
            )
            frames.append(Frame(frame_path, calibration_data.to_dict()))

        # bake pixel offsets into frames, smooth out angles
        Frame.compute_frame_offsets(frames)
        Frame.interpolate_angles(frames)

        image_stacker = get_image_stacker()
        image_stacker.light_frames = frames[:10]  # TODO use all frames, provide a range option
        image_stacker.stack_image()

        # Update hash in app state so FE can react by reloading the preview
        app_state = get_app_state()
        app_state.stacked_image_hash = image_stacker.get_stacked_image_hash()
        return ''


@api.route('/preview/<stacked_image_hash>')
class StackedImagePreviewApi(Resource):
    @api.doc(
        description='Get a preview image of the stacked image',
        response={200: 'Success'},
    )
    def get(self, stacked_image_hash):
        image_stacker = get_image_stacker()
        if image_stacker.get_stacked_image_hash() == stacked_image_hash:
            image_data_png = image_stacker.get_stacked_image(
                format='png',
                scale_factor=2
            )
            return send_file(image_data_png, mimetype='image/png')

        # TODO hash is outdated - maybe update it with whatever is new?
        return ''
