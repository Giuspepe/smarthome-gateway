import pytest
import json
import shelve
import api
import copy
import os

valid_mock_device_1 = {
        "device_id": "1234",
        "device_name": "Hue color lamp 1",
        "device_type": "Extended color light",
        "device_controller_address": "http://192.168.130.214/api/tAC901PfVfQMmNvrhc120uZeBa-Va8SNjc4vhtyh/1",
        "device_data": {
            "on": False,
            "bri": 254,
            "hue": 47104,
            "sat": 254,
            "effect": "none",
            "xy": [
                0.1532,
                0.0475
            ],
            "ct": 153,
            "alert": "select",
            "colormode": "xy",
            "mode": "homeautomation",
            "reachable": True
        }
    }
valid_mock_device_2 = copy.deepcopy(valid_mock_device_1)
valid_mock_device_2['device_id'] = '5678'


@pytest.fixture
def client():
    global shelve_db
    api.app.config['DATABASE'] = 'test_database'
    api.app.config['TESTING'] = True
    client = api.app.test_client()

    with api.app.app_context():
        shelve_db = shelve.open(api.app.config['DATABASE'])
        shelve_db['devices'] = [valid_mock_device_1, valid_mock_device_2]

    yield client

    shelve_db.close()
    os.remove('test_database.dat')
    os.remove('test_database.dir')
    os.remove('test_database.bak')


class TestDeviceListAPI:
    def test_get(self, client):
        # get device list
        rv = client.get('/devices')
        rv = json.loads(rv.data)

        assert rv == [valid_mock_device_1, valid_mock_device_2]

    def test_post_add_new_device(self, client):
        new_device = copy.deepcopy(valid_mock_device_1)
        new_device['device_id'] = 'new_id'
        rv = client.post('/devices', json=new_device)
        rv = json.loads(rv.data)

        assert '/devices/new_id' in rv['uri']
        del rv['uri']
        assert rv == new_device

    def test_post_add_device_with_existing_id(self, client):
        rv = client.post('/devices', json=valid_mock_device_1)
        rv = json.loads(rv.data)

        assert rv == f'Device with device_id \"{valid_mock_device_1["device_id"]}\" already exists'


class TestDeviceAPI:
    def test_get(self, client):
        # get device from existing device_id
        valid_device_id = valid_mock_device_1['device_id']
        rv = client.get(f'/devices/{valid_device_id}')
        rv = json.loads(rv.data)
        assert f'/devices/{valid_device_id}' in rv['uri']
        del rv['uri']
        assert rv == valid_mock_device_1

        # get device that doesn't exist
        rv = client.get('/devices/invalid_device_id')
        rv = json.loads(rv.data)
        assert f'There is no device with device_id "invalid_device_id"' in rv

    def test_patch(self, client):
        valid_device_id = valid_mock_device_1['device_id']
        simple_device_attributes = ['device_name', 'device_type', 'device_controller_address']
        for attribute in simple_device_attributes:
            rv = client.patch(f'/devices/{valid_device_id}', json={attribute: 'changed_attribute_value12345'})
            rv = json.loads(rv.data)
            assert rv[attribute] == 'changed_attribute_value12345'



        rv = client.patch(f'/devices/{valid_device_id}', json={'device_id': 'changed_device_id12345'})
        rv = json.loads(rv.data)
        assert rv['device_id'] == 'changed_device_id12345'
        client.patch(f'/devices/changed_device_id12345', json={'device_id': '1234'})

        changed_device_data = {
            "on": True,
            "bri": 1,
            "hue": 1,
            "sat": 1,
            "effect": "blabla",
            "xy": [
                0.1,
                0.2
            ],
            "ct": 3,
            "alert": "lala",
            "colormode": "z",
            "mode": "test",
            "reachable": False}

        rv = client.patch(f'/devices/{valid_device_id}', json={'device_data': changed_device_data})
        rv = json.loads(rv.data)
        assert rv == 'Device type "changed_attribute_value12345" not implemented yet'
        # TODO assert rv['device_data'] == changed_device_data

    def test_delete(self, client):
        # delete device
        device = copy.deepcopy(valid_mock_device_1)
        rv = client.delete(f'/devices/{device["device_id"]}')
        rv = rv.data
        assert 'Deleted device' in str(rv)
        devices = client.get('/devices')
        devices = json.loads(devices.data)
        assert devices == [valid_mock_device_2]

        # delete device that doesn't exist
        device = copy.deepcopy(valid_mock_device_1)
        rv = client.delete(f'/devices/{device["device_id"]}')
        rv = str(rv.data)
        assert f'There is no device with device_id' in rv


if __name__ == '__main__':
    pytest.main()
