# smarthome-gateway


## api.py
RESTful API for communication between Heroku Cloud and Raspberry Pi
Add, edit, and delete devices
Devices can be controlled by editing their state data


### Endpoint /devices

#### Get device list

**Method**

`GET /devices`

**Response**
- `200 OK``on success
```json
[
    {
        "device_id": "1",
        "device_name": "MOCK_Deckenlampe",
        "device_type": "MOCK_Philips Hue Color Ambiance",
        "device_controller_address": "https://123.123.123/api/api_token/lights/light_id",
        "device_data": "{\"on\": True, \"xy\": [0, 1]}"
    },
	...
]
```

#### Add new device

**Method**

`POST /devices`

following data must be given as json in the request body:
--* **device_id** (str): internal id, must be unique
--* **device_name** (str): display name
--* **device_type** (str): type of device, e.g. Philips Hue Color Ambiance
--* **device_controller_address** (str): address of the device's controller
--* **device_data** (str): json string containing all data on the device's state (e.g. `{"data": "{\"on\": \"True\"}"


**Response**

- `400 BAD REQUEST` if some piece of device information is missing

- `200 OK` on success
```json
{
    "uri": "/devices/thisisanid1234",
    "device_name": "my first device",
    "device_type": "super smart thing",
    "device_data": "{\"on\": \"True\"}"
}
```

### Endpoint /devices/<string:device_id>

#### Get device information
same as `GET /devices` but you only get data on the device with the given device_id

#### Edit device

**Method**
`PATCH /devices/<string:device_id>`
put the data you want to change in the request body as json (e.g. `{"device_name": "new fancy name"}`)

**Response**
returns all device data

#### Delete device
`DELETE /devices/<string:device_id>

**Response**
- `200 OK` and deleted device data on success
- `404 NOT FOUND` if there is no device with the given device_id