from flask import request
from flask.json import jsonify
from flask_restplus import Namespace, Resource

from hti.server.globals import get_indi_controller

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
        return jsonify(get_indi_controller().devices())


@api.route('/device_names')
class DeviceNamesApi(Resource):
    @api.doc(
        description='List device names',
        response={
            200: 'Success'
        }
    )
    def get(self):
        return jsonify({'devices': get_indi_controller().device_names()})


@api.route('/device/<devicename>/properties')
class DevicePropertiesListApi(Resource):
    @api.doc(
        description='List device properties',
        response={
            200: 'Success'
        }
    )
    def get(self, devicename):
        return jsonify(get_indi_controller().properties(devicename))


@api.route('/device/<devicename>/properties/<property>')
class DevicePropertyApi(Resource):
    @api.doc(
        description='Get device property',
        response={
            200: 'Success'
        }
    )
    def get(self, devicename, property):
        return jsonify(get_indi_controller().property(devicename, property))

    @api.doc(
        description='Set device property',
        response={
            200: 'Success'
        }
    )
    def put(self, devicename, property):
        return jsonify(get_indi_controller().set_property(devicename, property, request.json['value']))
