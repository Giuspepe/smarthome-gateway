import requests
import json
from time import sleep


def get_lights(api_root_url):
    lights = requests.get(api_root_url + 'lights').json()
    light_id_list = []
    for light_id, light_info in lights.items():
        light_id_list.append(light_id)
        print(f'Light id: {light_id} - Light name: {light_info["name"]}')
    return light_id_list


def get_light_info(api_light_url):
    return requests.get(api_light_url).json()


def set_state(api_light_url, state):
    return requests.put(f'{api_light_url}/state', json.dumps(state))


def turn_on(api_light_url):
    state = {'on': True}
    return set_state(api_light_url, state)


def turn_off(api_light_url):
    state = {'on': False}
    return set_state(api_light_url, state)

# def test_effect(light_id):
#     for x in range(0, 10):
#         for y in range(0,10):
#             set_state(light_id, {'xy': [x/10, y/10]})
#             sleep(0.1)
#
# def add_device(light_id):
#     # get light info from Hue API
#     light_info = get_light_info(light_id)
#     # use data to add new device
#     device = {
#         'device_id': light_id,
#         'device_name': light_info['name'],
#         'device_type': light_info['type'],
#         'device_controller_address': base_api_address + light_id,
#         'device_data': light_info['state']
#     }
#     return requests.post('http://localhost:5000/devices', json=device)


if __name__ == '__main__':
    print('main')
    # light_id_list = get_lights()
    # for light_id in light_id_list:
    #     print(add_device(light_id))
    #
        #turn_off(light_id)
    #sleep(3)
    #for light_id in light_id_list:
    #    turn_on(light_id)
    #    print(set_state(light_id, {'xy': [0, 0], 'sat': 254, 'bri': 254}).text)

    # test_effect(3)
