from ukie_core.PM101 import PolarisationOptimiser
from yqcinst.instruments.epc04 import EPC04, DeviceMode
from ukie_core.utils import load_config, validate_float
import idqube
import time
import numpy as np
import questionary


def alignment():
    config = load_config()
    qube1 = idqube.IDQube(config['Q1']['address'])
    qube2 = idqube.IDQube(config['Q2']['address'])

    qube1.set_detector_eff_temp_indexes(1, 1)
    qube2.set_detector_eff_temp_indexes(1, 1)
    time.sleep(3)

    print('The detection efficiency for Q1 is', qube1.detector_efficiency)
    print('The detection efficiency for Q2 is', qube2.detector_efficiency)

    epc = EPC04(config['epc']['address'])
    epc.device_mode = DeviceMode.DC

    target_er = float(
        questionary.text(
            '\nInput target extinction ratio (dB)',
            validate=validate_float
        )
    )

    po = PolarisationOptimiser(
        **config['po_args']['alignment'],
        epc=epc
    )

    po.run()


def measurement():
    config = load_config()
    qube1 = idqube.IDQube(config['Q1']['address'])
    qube2 = idqube.IDQube(config['Q2']['address'])

    qube1.set_detector_eff_temp_indexes(4, 1)
    qube2.set_detector_eff_temp_indexes(4, 1)
    time.sleep(3)

    print('Initial count for Q1', qube1.photon_count)
    print('Initial count for Q2', qube2.photon_count)

    qube1_counts = []
    qube2_counts = []

    start = time.time()
    while time.time() - start < 600:
        qube1_counts.append(qube1.photon_count)
        qube2_counts.append(qube2.photon_count)

    filename = input('Input a (safe) filename for output data')
    np.savetxt(
        filename,
        (
            (qube1_counts),
            (qube2_counts)
        ),
        delimiter=','
    )


def quit():
    raise KeyboardInterrupt


processes = {
    'alignment': alignment,
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
