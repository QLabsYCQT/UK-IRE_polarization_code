from yqcinst.instruments.epc04 import EPC04
from ukie_core.server_listener import ServerListener
from ukie_core.utils import load_config
from yqcinst.instruments.keithley2231a import Keithley2231A
from ukie_core.pax1000IR2 import PAX1000IR2
from ukie_core.polopt import PAX1000IR2PolarisationOptimiser as PolOpt
import questionary


def listen():
    config = load_config()
    sl = ServerListener(**config['server'])
    epc = EPC04(config['epc']['address'])
    polarimeter = PAX1000IR2(address='USB0::0x1313::0x8031::M00920880::INSTR')
    po = PolOpt(
        **config['po_args']['alignment'],
        epc=epc,
        polarimeter=polarimeter,
    )
    sl.instruments = {
        'epc': epc,
        'epc_ch1': epc.channels[0],
        'epc_ch2': epc.channels[1],
        'epc_ch3': epc.channels[2],
        'epc_ch4': epc.channels[3],
        'keithley': Keithley2231A(config['keithley']['address']),
        'po': po
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
