from yqcinst.instruments.epc04 import EPC04, DeviceMode
from ukie_core.polopt import KoheronPolarisationOptimiser as PolOpt
from ukie_core.koheronDetector import koheronDetector
from ukie_core.utils import load_config
import questionary
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import nidaqmx


def alignment():
    config = load_config()

    epc = EPC04(config['epc']['address'])
    epc.device_mode = DeviceMode.DC

    koheron = koheronDetector()
    po = PolOpt(
        **config['po_args'],
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


def quit():
    raise KeyboardInterrupt


processes = {
    'alignment': alignment,
    'monitor power': monitor_power,
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
