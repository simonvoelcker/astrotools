import argparse

from flask import Flask
from flask_cors import CORS

from hti.server.config import Production
from hti.server.client import api_blueprint, client_blueprint
from hti.server.state.globals import get_camera_controller, get_axis_control

app = Flask(__name__)
CORS(app)

config = Production
app.register_blueprint(api_blueprint)
app.register_blueprint(client_blueprint)
app.config.from_object(config)
app.secret_key = app.config['FLASK_SECRET_KEY']

get_camera_controller()
get_axis_control()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    app.run(host=app.config['FLASK_HOST'], port=app.config['FLASK_PORT'], debug=app.config['FLASK_DEBUG'])
