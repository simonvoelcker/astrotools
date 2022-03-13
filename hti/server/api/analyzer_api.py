from flask_restplus import Namespace, Resource
from flask.json import jsonify

from hti.server.frames_db import FramesDB
from hti.server.state.events import sequences_event

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
        sequences_event(frames_db.list_sequences())
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

# Next up:
# Basic UI which lists sequences
# An endpoint to trigger the analysis on all frames of a sequence
# and write the analysis result to the DB. Fork analyze.py for this.
