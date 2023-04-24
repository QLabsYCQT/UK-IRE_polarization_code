from ukie_core.EPC04 import EPCDriver
from ukie_core.server_listener import ServerListener
from yqcinst.instruments.keithley2231a import Keithley2231A
import json
import questionary
import os


def load_config():
    config_path = os.environ.get('UKIE_CONFIG_FILE')
    if config_path is None:
        config_path = questionary.path(
            'Please provide the path to the config file: ',
            default='config.json'
        ).ask()
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config


def listen():
    config = load_config()
    sl = ServerListener(**config['server'])
    sl.instruments = {
        'epc': EPCDriver(config['epc']['address']),
        'keithley': Keithley2231A(config['keithley']['address'])
    }
    try:
        while True:
            pass
    except KeyboardInterrupt:
        sl.stop_thread = True


def quit():
    raise KeyboardInterrupt


processes = {
    'listen for remote instructions': listen,
    'quit': quit
}


menu = questionary.select(
    '\nPlease choose a process to run: ',
    choices=list(processes.keys())
)

try:
    while True:
        process = menu.ask()
        try:
            processes[process]()
        except Exception as e:
            print(f'An exception occured whilst executing process {process}:')
            print(f'{repr(e)}')
except KeyboardInterrupt:
    pass
