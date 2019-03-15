# TODO: more endpoints? /devices/huelights, /devices/sensors, /devices/whatever ?

from flask import Flask
from flask_restful import Api, Resource, reqparse, fields, marshal
import shelve
import functools
import copy
import json
from control_hue_lights import set_state

app = Flask(__name__)
api = Api(app)

api.app.config['DATABASE'] = 'database_shelve'

device_attributes = ['device_id', 'device_name', 'device_type', 'device_controller_address', 'device_data']

def shelve_db_decorator(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        global shelve_db  # global is necessary, otherwise func can't see shelve_db
        # opens and closes shelve database automatically even if an exception is raised
        with shelve.open(api.app.config['DATABASE'], writeback=True) as shelve_db:
            rv = func(*args, **kwargs)
        return rv
    return inner


class DeviceListAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('device_id', type=str, required=True,
                                   help='No/invalid device_id provided', location='json')
        self.reqparse.add_argument('device_name', type=str, required=True,
                                   help='No/invalid device_name provided', location='json')
        self.reqparse.add_argument('device_type', type=str, required=True,
                                   help='No/invalid device_type provided', location='json')
        self.reqparse.add_argument('device_controller_address', type=str, required=True,
                                   help='No/invalid device_controller_address provided', location='json')
        self.reqparse.add_argument('device_data', type=dict, required=True,
                                   help='No/invalid device_data provided', location='json')
        super(DeviceListAPI, self).__init__()

    @shelve_db_decorator
    def get(self):
        return shelve_db['devices'], 200

    @shelve_db_decorator
    def post(self):
        args = self.reqparse.parse_args()

        if [device for device in shelve_db['devices'] if device['device_id'] == args['device_id']]:
            return f'Device with device_id "{args["device_id"]}" already exists', 409

        new_device = {
            'device_id': args['device_id'],
            'device_name': args['device_name'],
            'device_type': args['device_type'],
            'device_controller_address': args['device_controller_address'],
            'device_data': args['device_data']
        }
        shelve_db['devices'].append(new_device)
        return marshal(new_device, device_fields), 200


device_fields = {
    'uri': fields.Url('device', absolute=True),
    'device_id': fields.String,
    'device_name': fields.String,
    'device_type': fields.String,
    'device_controller_address': fields.String,
    'device_data': fields.Raw
}


class DeviceAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('device_id', type=str, location='json')
        self.reqparse.add_argument('device_name', type=str, location='json')
        self.reqparse.add_argument('device_type', type=str, location='json')
        self.reqparse.add_argument('device_controller_address', type=str, location='json')
        self.reqparse.add_argument('device_data', type=dict, location='json')
        super(DeviceAPI, self).__init__()

    @shelve_db_decorator
    def get(self, device_id):
        device = [device for device in shelve_db['devices'] if device['device_id'] == device_id]
        if len(device) == 0:
            # device not found
            return f'There is no device with device_id "{device_id}"', 404
        if len(device) == 1:
            # device found
            return marshal(device[0], device_fields), 200
        if len(device) > 1:
            return f'Found {len(device)} devices with the same device_id', 500

    @shelve_db_decorator
    def patch(self, device_id):
        # get copy of device you want to edit
        device = [device for device in enumerate(shelve_db['devices']) if device[1]['device_id'] == device_id]
        device_index = device[0][0]
        device = copy.deepcopy(device[0][1])

        # check input
        args = self.reqparse.parse_args()
        # TODO: don't need this because regparse ensures that you can only enter device_id, device_name, device_type,...
        if not set(list(args.keys())).issubset(device_attributes):
            invalid_attributes = set(device_attributes) - set(list(args.keys()))
            return f'You provided invalid attributes: {invalid_attributes}', 400

        # 0. close db
        for key, val in args.items():
            if val is not None:
                if key != 'device_data':
                    # change 'device_id', 'device_name', 'device_type', 'device_controller_address'
                    device[key] = val
                else:
                    # change hardware data (e.g. color of a light)
                    if 'Hue' in device['device_type']:
                        # TODO: call hue api
                        # 1. call respective API with data to be changed
                        print('set state')
                        print(key, val)
                        #set_state(device_id, {key: val})
                        pass
                    elif 'another device type' in device['device_type']:
                        # TODO: to be implemented
                        # 0. close db?
                        # 1. call respective API with data to be changed
                        # 2. call respective API to get new device data
                        # 3. open db again?
                        # 4. write changed device data back to device
                        pass
                    elif 'custom device' in device['device_type']:
                        # TODO: to be implemented
                        # 0. close db?
                        # 1. call respective API with data to be changed
                        # 2. call respective API to get new device data
                        # 3. open db again?
                        # 4. write changed device data back to device
                        pass
                    else:
                        return f'Device type "{device["device_type"]}" not implemented yet', 400

        # 2. call respective API to get new device data
        # if 'Hue' in device['device_type']:
        #     new_device_data = get(/lights/device_id) oder:
        #     new_device_data = get_light_info(device_id)
        #     new_device_data = new_device_data['state']
        # elif 'another device type' in device['device_type']:
        #     new_device_data = get(...)
        # ...

        # 3. open db again
        # 4. device['device_data'] = new_device_data

        # write back edited copy
        shelve_db['devices'][device_index] = device
        return marshal(device, device_fields), 200

    @shelve_db_decorator
    def delete(self, device_id):
        device = [device for device in enumerate(shelve_db['devices']) if device[1]['device_id'] == device_id]
        if device:
            device_index = device[0][0]
            device = device[0][1]
            del shelve_db['devices'][device_index]
            return f'Deleted device {device}', 200
        else:
            return f'There is no device with device_id "{device_id}"', 404


api.add_resource(DeviceListAPI, '/devices', endpoint='devices')
api.add_resource(DeviceAPI, '/devices/<device_id>', endpoint='device')

if __name__ == '__main__':
    app.run(debug=True)
