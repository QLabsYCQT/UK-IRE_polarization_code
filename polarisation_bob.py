from yqcinst.instruments.osw22 import OSW22, SwitchState
from yqcinst.instruments.epc04 import EPC04, DeviceMode as EPCDeviceMode
from yqcinst.instruments.keithley2231a import Keithley2231A, DeviceMode as KeithleyDeviceMode
from ukie_core.polopt import (KoheronERPolarisationOptimiser as KPolOpt,
                              PAX1000IR2PolarisationOptimiser as PPolOpt,
                              convert_angle)
from ukie_core.koheronDetector import koheronDetector
from ukie_core.utils import load_config, validate_int
from ukie_core.remote_instrument import remote_instrument
import questionary
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import nidaqmx
from time import sleep


RemoteKeithley = remote_instrument(Keithley2231A, 'keithley')
RemotePolOpt = remote_instrument(PPolOpt, 'po')


def align_remote():
    config = load_config()

    azimuth = int(
        questionary.text(
            'Input integer target azimuth ψ in (-90°, 90°]',
            validate=validate_int
        ).ask()
    )
    ellipticity = int(
        questionary.text(
            'Input integer target ellipticity χ in (-45°, 45°]',
            validate=validate_int
        ).ask()
    )

    po = RemotePolOpt(**config['server'])
    po.target_azimuth = convert_angle(azimuth)
    po.target_ellipticity = convert_angle(ellipticity)

    po.initialisation()
    po.gradient_search()



def align_local():
    config = load_config()
    sw1 = OSW22(config['osw22']['addresses'][0])
    sw2 = OSW22(config['osw22']['addresses'][1])
    sw1.switch_state = SwitchState.BAR
    sw2.switch_state = SwitchState.BAR
    assert sw1.switch_state == SwitchState.BAR
    assert sw2.switch_state == SwitchState.BAR

    remote_keithley = RemoteKeithley(**config['server'])
    remote_keithley.mode = KeithleyDeviceMode.REMOTE
    remote_keithley.enabled = [True, True, True]
    remote_keithley.voltage = [0, 0, 0]

    epc = EPC04(config['epc']['address'])
    epc.device_mode = EPCDeviceMode.DC

    koheron = koheronDetector()
    po = KPolOpt(
        **config['po_args']['bob'],
        epc=epc,
        detector=koheron,
    )

    po.initialisation()
    po.gradient_search()

def monitor_power():
    config = load_config()
    voltage_min, voltage_max = config['acquisition']['voltage limits']

    fig, ax = plt.subplots(1, 1)
    ai0 = Line2D([], [], color='blue', label='ai0')
    ai1 = Line2D([], [], color='orange', label='ai1')
    ax.add_line(ai0)
    ax.add_line(ai1)
    ax.set_xlabel('time / s')
    ax.set_ylabel('voltage / V')
    ax.set_xlim(0, 10)
    ax.set_ylim(voltage_min, voltage_max)
    ax.legend(loc='upper right')

    with nidaqmx.Task('Read PD1') as task:
        task.ai_channels.add_ai_voltage_chan(
            'Dev1/ai0',
            min_val=voltage_min,
            max_val=voltage_max)
        task.ai_channels.add_ai_voltage_chan(
            'Dev1/ai1',
            min_val=voltage_min,
            max_val=voltage_max)
        task.timing.cfg_samp_clk_timing(
            2_000,
            sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
        stream = task.in_stream
        reader = nidaqmx.stream_readers.AnalogMultiChannelReader(stream)
        task.start()
        data = np.zeros((2, 200))
        history = np.zeros((2, 20_000))
        t = np.linspace(0, 10, 20_000)
        fig.canvas.draw()
        try:
            while True:
                reader.read_many_sample(
                    data,
                    200,
                    timeout=nidaqmx.constants.WAIT_INFINITELY)
                history = np.roll(history, 200, axis=1)
                history[:,:200] = data
                ai0.set_data(t, history[0])
                ai1.set_data(t, history[1])
                fig.canvas.draw()
                plt.pause(0.01)
        except KeyboardInterrupt:
            task.stop()


def measurement():
    config = load_config()
    voltage_min, voltage_max = config['acquisition']['phase']['voltage limits']
    sw1 = OSW22(config['osw22']['addresses'][0])
    sw2 = OSW22(config['osw22']['addresses'][1])
    sw1.switch_state = SwitchState.BAR
    sw2.switch_state = SwitchState.BAR
    with nidaqmx.Task('Read PD1') as task:
        task.ai_channels.add_ai_voltage_chan(
            'Dev1/ai0',
            min_val=voltage_min,
            max_val=voltage_max)
        task.ai_channels.add_ai_voltage_chan(
            'Dev1/ai1',
            min_val=voltage_min,
            max_val=voltage_max)
        task.timing.cfg_samp_clk_timing(
            2_000,
            sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
        stream = task.in_stream
        reader = nidaqmx.stream_readers.AnalogMultiChannelReader(stream)
        task.start()
        data = np.zeros((2, 200))
    remote_keithley = RemoteKeithley(**config['server'])
    remote_keithley.mode = KeithleyDeviceMode.REMOTE
    remote_keithley.enabled = [True, True, True]
    remote_keithley.voltage = config['acquisition']['polarisation']['EVOA voltages']
    assert remote_keithley.voltage == [0.0, 4.05, 5.0]
    if questionary.confirm(
        'Send light to SNSPD?',
    ).ask():
        for i in range(5):
            print(f'Light on SNSPD in {5-i}s')
            sleep(1)
        sw1.switch_state = SwitchState.CROSS
        sw2.switch_state = SwitchState.CROSS

        questionary.confirm(
            'Finished measurement?',
        ).ask()
    else:
        print('Cancelling measurement setup')

    sw1.switch_state = SwitchState.BAR
    sw2.switch_state = SwitchState.BAR


def quit():
    raise KeyboardInterrupt


processes = {
    'align remote': align_remote,
    'align local': align_local,
    'monitor power': monitor_power,
    'measurement': measurement,
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
