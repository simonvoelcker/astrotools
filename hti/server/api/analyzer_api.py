import os

from flask_restplus import Namespace, Resource
from flask.json import jsonify

from hti.server.api.util import find_frame_path
from hti.server.frames_db import FramesDB
from hti.server.state.globals import get_app_state
from hti.server.state.events import log_event

from lib.calibration_analyzer import CalibrationAnalyzer
from lib.frame_quality_analyzer import FrameQualityAnalyzer
from lib.frame import Frame


api = Namespace('Analyzer', description='Analyzer API endpoints')


@api.route('/sequences/')
class SequenceListApi(Resource):
    @api.doc(
        description='List all sequences',
        response={200: 'Success'},
    )
    def get(self):
        frames_db = FramesDB()
        sequences = frames_db.list_sequences()
        return jsonify(sequences)


@api.route('/sequences/<sequence_id>')
class SequenceDetailApi(Resource):
    @api.doc(
        description='Delete sequence',
        response={200: 'Success'},
    )
    def delete(self, sequence_id):
        frames_db = FramesDB()
        # Delete frames on disk first
        frames = frames_db.list_frames(sequence_id)
        for frame in frames:
            frame_path = find_frame_path(frame["filename"])
            os.remove(frame_path)
        # Delete DB entries for sequence and files
        frames_db.delete_sequence(sequence_id)
        return ''


@api.route('/sequences/<sequence_id>/frames/')
class SequenceFramesApi(Resource):
    @api.doc(
        description='List all frames in a sequence',
        response={200: 'Success'},
    )
    def get(self, sequence_id):
        frames_db = FramesDB()
        frames = frames_db.list_frames(sequence_id)
        return jsonify(frames)


@api.route('/sequences/<sequence_id>/analyze')
class AnalyzeSequenceApi(Resource):
    @api.doc(
        description='Analyze all frames of the sequence',
        response={200: 'Success'},
    )
    def post(self, sequence_id):
        frames_db = FramesDB()
        frames = frames_db.list_frames(sequence_id)

        app_state = get_app_state()
        app_state.analyzing = True

        for index, frame_info in enumerate(frames):
            log_event(f'Analyzing frame {index+1}/{len(frames)}')

            frame_path = find_frame_path(frame_info["filename"])
            frame = Frame(frame_path)

            frame_quality_analyzer = FrameQualityAnalyzer()
            frame_quality_analyzer.analyze_frame(frame)
            frame_quality = frame_quality_analyzer.get_results_dict(frame)

            calibration_analyzer = CalibrationAnalyzer()
            calibration_analyzer.analyze_frame(frame)
            calibration_data = calibration_analyzer.calibration_data[frame]

            frames_db.add_analysis(
                frame_id=frame_info["id"],
                calibration_data=calibration_data,
                brightness=frame_quality["brightness"],
                hfd=frame_quality["hfd"],
            )

        app_state.analyzing = False
        return ''


@api.route('/frames/<frame_id>')
class FramesApi(Resource):
    @api.doc(
        description='Delete frame',
        response={200: 'Success'},
    )
    def delete(self, frame_id):
        frames_db = FramesDB()
        filename = frames_db.get_frame_filename(frame_id)
        frame_path = find_frame_path(filename)
        # Remove file in DB
        frames_db.delete_frame(frame_id)
        # Remove file on disk
        os.remove(frame_path)
        return ''


@api.route('/frames/<frame_id>/path')
class FramePathApi(Resource):
    @api.doc(
        description='Get frame filepath',
        response={200: 'Success'},
    )
    def get(self, frame_id):
        frames_db = FramesDB()
        filename = frames_db.get_frame_filename(frame_id)
        frame_path = find_frame_path(filename)
        # Make path relative to static dir
        here = os.path.dirname(os.path.abspath(__file__))
        hti_static_dir = os.path.join(here, '..', 'static')
        relpath = os.path.relpath(frame_path, hti_static_dir)
        return relpath


@api.route('/frames/<frame_id>/analyze')
class AnalyzeFrameApi(Resource):
    @api.doc(
        description='Analyze the frame',
        response={200: 'Success'},
    )
    def post(self, frame_id):
        frames_db = FramesDB()
        filename = frames_db.get_frame_filename(frame_id)
        frame_path = find_frame_path(filename)
        frame = Frame(frame_path)

        app_state = get_app_state()
        app_state.analyzing = True

        frame_quality_analyzer = FrameQualityAnalyzer()
        frame_quality_analyzer.analyze_frame(frame)
        frame_quality = frame_quality_analyzer.get_results_dict(frame)

        calibration_analyzer = CalibrationAnalyzer()
        calibration_analyzer.analyze_frame(frame)
        calibration_data = calibration_analyzer.calibration_data[frame]

        frames_db.add_analysis(
            frame_id=frame_id,
            calibration_data=calibration_data,
            brightness=frame_quality["brightness"],
            hfd=frame_quality["hfd"],
        )

        app_state.analyzing = False
        return ''
