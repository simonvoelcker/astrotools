from flask_restplus import Namespace, Resource
from flask.json import jsonify

from hti.server.frames_db import FramesDB

api = Namespace('Analyzer', description='Analyzer API endpoints')


@api.route('/sequences/')
class SequencesApi(Resource):
    @api.doc(
        description='List all sequences',
        response={200: 'Success'},
    )
    def get(self):
        frames_db = FramesDB()
        sequences = frames_db.list_sequences()
        return jsonify(sequences)


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
# The endpoint which delivers the frame (image data)
# An endpoint to trigger the analysis on one frame
# An endpoint to trigger the analysis on all frames of a sequence
# An endpoint to get the analysis result
# Then we can build a UI
