from flask_restplus import Namespace, Resource
from flask import request

from hti.server.api.util import find_frame_path

from hti.server.frames_db import FramesDB
from lib.frame import Frame
from lib.image_stack import ImageStack
from lib.solver import CalibrationData
from lib.coordinates import Coordinates

api = Namespace('Stacking', description='Stacking API endpoints')


@api.route('/stack')
class StackApi(Resource):
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

        image = ImageStack.stack_frames(
            frames=frames,
            color_mode='rgb',
            master_dark=None,
            master_flat=None,
        )
        image.normalize()
        image.save(f'out/stacked_using_hti.png')

        return ''
