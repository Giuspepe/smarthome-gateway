# TODO: remove marshal? if not implement it in all functions that return a device

from flask import Flask
from flask_restful import Api, Resource, reqparse, fields, marshal
import shelve
import functools

app = Flask(__name__)
api = Api(app)


def db_shelve_decorator(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        global db_shelve  # global is necessary, otherwise func can't see db_shelve
        with shelve.open('database_shelve', writeback=True) as db_shelve:  # opens and closes shelve automatically
            rv = func(*args, **kwargs)
        return rv
    return inner


class DeviceListAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('device_id', type=str, required=True, help='No device_id provided', location='json')
        self.reqparse.add_argument('device_name', type=str, required=True,
                                   help='No device_name provided', location='json')
        self.reqparse.add_argument('device_type', type=str, required=True,
                                   help='No device_type provided', location='json')
        self.reqparse.add_argument('device_controller_address', type=str, required=True,
                                   help='No device_controller_address provided', location='json')
        self.reqparse.add_argument('device_data', type=str, required=True,
                                   help='No device_data provided', location='json')
        super(DeviceListAPI, self).__init__()

    @db_shelve_decorator
    def get(self):
        return db_shelve['devices'], 200

    @db_shelve_decorator
    def post(self):
        args = self.reqparse.parse_args()

        if args['device_id'] in list(db_shelve.keys()):
            return f'Device with device_id {args["device_id}"]} already exists', 409

        new_device = {
            'device_id': args['device_id'],
            'device_name': args['device_name'],
            'device_type': args['device_type'],
            'device_controller_address': args['device_controller_address'],
            'device_data': args['device_data']
        }
        db_shelve['devices'].append(new_device)
        return marshal(new_device, device_fields), 200


device_fields = {
    'uri': fields.Url('device'),
    'device_name': fields.String,
    'device_type': fields.String,
    'device_data': fields.String
}


class DeviceAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('device_id', type=str, location='json')
        self.reqparse.add_argument('device_name', type=str, location='json')
        self.reqparse.add_argument('device_type', type=str, location='json')
        self.reqparse.add_argument('device_controller_address', type=str, location='json')
        self.reqparse.add_argument('device_data', type=str, location='json')
        super(DeviceAPI, self).__init__()

    @db_shelve_decorator
    def get(self, device_id):
        device = [device for device in db_shelve['devices'] if device['device_id'] == device_id]
        if len(device) == 0:
            # device not found
            return f"Couldn't find device with id {device_id}", 404
        if len(device) == 1:
            # device found
            return device[0], 200
        # TODO: remove this? it's not possible to add devices with an already existing device_id
        if len(device) > 1:
            return f"Found {len(device)} devices with the same device_id", 500

    @db_shelve_decorator
    def patch(self, device_id):
        # get copy of device you want to edit
        device = [device for device in enumerate(db_shelve['devices']) if device[1]['device_id'] == device_id]
        device_index = device[0][0]
        device = device[0][1]

        # edit copy
        args = self.reqparse.parse_args()
        for k, v in args.items():
            if v is not None:
                device[k] = v

        # write edited copy back
        db_shelve['devices'][device_index] = device

        return marshal(device, device_fields), 200
        # TODO: bei Verändern einer Geräteeigenschaft zum Zweck der Steuerung muss nach dem Schließen des shelves
        # TODO: diese Veränderung dem Steuerprogramm mitgeteilt werden damit die Änderung umgesetzt werden kann
        # TODO: (also z.B. Lampe anschalten). Sonst müsste das Steuerprogramm die shelve immer pollen auf Änderungen

    @db_shelve_decorator
    def delete(self, device_id):
        device = [device for device in enumerate(db_shelve['devices']) if device[1]['device_id'] == device_id]
        if device:
            device_index = device[0][0]
            device = device[0][1]
            del db_shelve['devices'][device_index]
            return f'Deleted device {device}', 200
        else:
            return f'There is no device with device_id {device_id}', 404


api.add_resource(DeviceListAPI, '/devices', endpoint='devices')
api.add_resource(DeviceAPI, '/devices/<device_id>', endpoint='device')

if __name__ == '__main__':
    app.run(debug=True)
