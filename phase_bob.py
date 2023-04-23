from ukie_core.koheronOptimisation import PolarisationOptimiser
from ukie_core.EPC04 import EPCDriver
from yqcinst.instruments.keithley2231a import Keithley2231A, DeviceMode
from ukie_core.remote_instrument import remote_instrument
import json
import questionary
import nidaqmx
import numpy as np
import time
import os

RemoteEPCDriver = remote_instrument(EPCDriver, 'epc')
RemoteKeithley = remote_instrument(Keithley2231A, 'keithley')


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


def align_local():
    config = load_config()
    local_epc = EPCDriver(config['epc']['address'])
    print(config['po_args'])
    po = PolarisationOptimiser(**config['po_args'], epc=local_epc)
    po.initialisation()
    po.gradientSearch()


def align_remote():
    config = load_config()
    remote_epc = RemoteEPCDriver()

    remote_keithley = RemoteKeithley(**config['server'])
    remote_keithley.mode = DeviceMode.REMOTE
    remote_keithley.enabled = [True, True, True]
    remote_keithley.voltage = [5, 5, 5]
    po = PolarisationOptimiser(**config['po_args'], epc=remote_epc)
    po.epc = remote_epc
    po.initialisation()
    po.gradientSearch()


def acquire_data():
    with nidaqmx.Task('Read PD1') as task:
        task.ai_channels.add_ai_voltage_chan(
            'Dev1/ai0',
            min_val=0,
            max_val=5)
        task.ai_channels.add_ai_voltage_chan(
            'Dev1/ai1',
            min_val=0,
            max_val=5)
        task.timing.cfg_samp_clk_timing(
            2_000_000,
            sample_mode=nidaqmx.constants.AcquisitionType.FINITE,
            samps_per_chan=32_000_000)
        stream = task.in_stream
        reader = nidaqmx.stream_readers.AnalogMultiChannelReader(stream)
        task.start()
        data = np.zeros((2, 32_000_000))
        reader.read_many_sample(
            data,
            nidaqmx.constants.READ_ALL_AVAILABLE,
            timeout=nidaqmx.constants.WAIT_INFINITELY)
        task.stop()
        filename = f'phase-acquisition-{time.time()}'
        np.save(filename, data)


def quit():
    raise KeyboardInterrupt


processes = {
    'local EPC alignment': align_local,
    'remote EPC alignment': align_remote,
    'data acquisition': acquire_data,
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
