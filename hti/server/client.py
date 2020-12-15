from flask import Blueprint, render_template
from flask_restplus import Api

from hti.server.api.camera_api import api as camera_api
from hti.server.api.axes_api import api as axes_api
from hti.server.api.info_api import api as info_api
from hti.server.api.indi_api import api as indi_api
from hti.server.api.guiding_api import api as guiding_api

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

api = Api(api_blueprint, title='Telescope API', version='1.0.0', description='Telescope API', doc='/doc/')
api.add_namespace(camera_api, path='/camera')
api.add_namespace(axes_api, path='/axes')
api.add_namespace(info_api, path='/info')
api.add_namespace(indi_api, path='/indi')
api.add_namespace(guiding_api, path='/guiding')
