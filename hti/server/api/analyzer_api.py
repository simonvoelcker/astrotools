import os

from flask_restplus import Namespace, Resource
from flask.json import jsonify

from hti.server.frames_db import FramesDB

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
        frames_db.delete_sequence(sequence_id)
        return ''


@api.route('/sequences/<sequence_id>/frames/')
class FramesApi(Resource):
    @api.doc(
        description='List all frames in a sequence',
        response={200: 'Success'},
    )
    def get(self, sequence_id):
        frames_db = FramesDB()
        frames = frames_db.list_frames(sequence_id)
        return jsonify(frames)


@api.route('/frames/<frame_id>/path')
class FramePathApi(Resource):

    @staticmethod
    def find_file(name, path):
        for root, dirs, files in os.walk(path):
            if name in files:
                return os.path.join(root, name)
        return None

    @api.doc(
        description='Get frame filepath',
        response={200: 'Success'},
    )
    def get(self, frame_id):
        frames_db = FramesDB()
        filename = frames_db.get_frame_filename(frame_id)
        # Find the file in static dir
        here = os.path.dirname(os.path.abspath(__file__))
        hti_static_dir = os.path.join(here, '..', 'static')
        path = self.find_file(filename, hti_static_dir)
        relpath = os.path.relpath(path, hti_static_dir)
        return relpath