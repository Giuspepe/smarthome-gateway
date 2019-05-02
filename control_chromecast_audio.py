import subprocess
import sys

if 'win' in sys.platform:
    chromecast_script_name = 'chromecast.exe'
else:
    chromecast_script_name = 'chromecast'


def update(device, device_data):
    host = device['device_controller_address']
    port = device['device_data']['port']
    radio_address = device['device_data']['radio_station_url']
    volume = device['device_data']['volume']
    base_command = [chromecast_script_name, '--host={}'.format(host), '--port={}'.format(port)]

    # change volume
    if 'volume' in device_data:
        subprocess.Popen(base_command + ['volume', volume], stdout=subprocess.DEVNULL)

    # change state
    if 'state' in device_data or 'radio_address' in device_data:
        state = device['device_data']['state']
        if state == 'playing':
            subprocess.Popen(base_command + ['media', 'play', radio_address], stdout=subprocess.DEVNULL)
        else:
            subprocess.Popen(base_command + ['quit'], stdout=subprocess.DEVNULL)


