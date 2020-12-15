from flask import request
from flask.json import jsonify
from flask_restplus import Namespace, Resource

from hti.server.state.globals import get_camera_controller

api = Namespace('INDI', description='INDI API')


@api.route('/devices')
class DevicesApi(Resource):
    @api.doc(
        description='List devices',
        response={
            200: 'Success'
        }
    )
    def get(self):
        return jsonify(get_camera_controller().devices())


@api.route('/device/<devicename>/properties')
class DevicePropertiesListApi(Resource):
    @api.doc(
        description='List device properties',
        response={
            200: 'Success'
        }
    )
    def get(self, devicename):
        return jsonify(get_camera_controller().properties(devicename))


@api.route('/device/<devicename>/properties/<property>')
class DevicePropertyApi(Resource):
    @api.doc(
        description='Get device property',
        response={
            200: 'Success'
        }
    )
    def get(self, devicename, property):
        return jsonify(get_camera_controller().property(devicename, property))

    @api.doc(
        description='Set device property',
        response={
            200: 'Success'
        }
    )
    def put(self, devicename, property):
        return jsonify(get_camera_controller().set_property(devicename, property, request.json['value']))
