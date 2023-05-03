from ukie_core.EPC04 import EPCDriver
from ukie_core.server_listener import ServerListener
from ukie_core.utils import load_config
from yqcinst.instruments.keithley2231a import Keithley2231A
import questionary


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
