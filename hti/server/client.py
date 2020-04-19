from flask import Blueprint, render_template
from flask_restplus import Api

from server.api.camera_api import api as camera_api

client_blueprint = Blueprint(
    'client_app',
    __name__,
    url_prefix='',
    static_url_path='static',
    static_folder='static',
    template_folder='templates',
)

@client_blueprint.route('/')
def index():
    return render_template('index.html')

api_blueprint = Blueprint(
    'api',
    __name__,
    url_prefix='/api'
)

api = Api(api_blueprint, title='Camera API', version='1.0.0', description='API of the camera', doc='/doc/')
api.add_namespace(camera_api, path='/camera')
