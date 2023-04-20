from ukie_core.EPC04 import EPCDriver
from ukie_core.server_listener import ServerListener
from yqcinst.instruments.keithley2231a import Keithley2231A
import json
import questionary


def load_config(config=None):
    with open('config.json', 'r') as f:
        config = json.load(f)
    return config


def listen(config):
    sl = ServerListener(**config['server'])
    sl.instruments += {
        'epc': EPCDriver(config['epc']['address']),
        'keithley': Keithley2231A(config['keithley']['address'])
    }
    return sl


def quit(config):
    raise KeyboardInterrupt


processes = {
    'load config': load_config,
    'listen for remote instructions': listen,
    'quit': quit
}


menu = questionary.select(
    '\nPlease choose a process to run: ',
    choices=list(processes.keys())
)

config = load_config()
try:
    while True:
        process = menu.ask()
        try:
            processes[process](config)
        except Exception as e:
            print(f'An exception occured whilst executing process {process}:')
            print(f'{repr(e)}')
except KeyboardInterrupt:
    pass
