from yqcinst.instruments.epc04 import EPC04
from ukie_core.polopt import PAX1000IR2PolarisationOptimiser as PolOpt
from ukie_core.utils import load_config, validate_int
from ycqinst.instruments.keithley2231a import Keithley2231A, DeviceMode
import questionary


def alignment():
    config = load_config()
    keithley = Keithley2231A(config['keithley']['address'])
    keithley.mode = DeviceMode.REMOTE
    keithley.enabled = [True, True, True]
    keithley.voltage = [5, 2, 0]

    epc = EPC04(config['epc']['address'])
    po = PolOpt(
        **config['po_args']['alignment']['initial'],
        epc=epc
    )

    po.run()

    while po.function > po.angleThreshold:
        po = PolOpt(
            **config['po_args']['alignment']['subsequent'],
            epc=epc
        )
        po.run()
    po.polarimeter.measureOnce()

    azimuth = po.PolM.dataDic['azimuth']
    ellipticity = po.PolM.dataDic['ellipticity']

    print(f'Azimuth ψ = {azimuth}°')
    print(f'Ellipticity χ = {ellipticity}°')


def state_generation():
    config = load_config()
    azimuth = int(
        questionary.text(
            '\nInput integer target azimuth ψ ∈ (-90°, 90°]',
            validate=validate_int
        )
    )
    ellipticity = int(
        questionary.text(
            '\nInput integer target ellipticity χ ∈ (-45°, 45°]',
            validate=validate_int
        )
    )

    epc = EPC04(config['epc']['address'])

    po = PolOpt(
        **config['po_args']['state_generation']['initial'],
        targetAzimuth=azimuth,
        targetEllipticity=ellipticity,
        epc=epc
    )

    po.run()

    while po.function > po.angleThreshold:
        po = PolOpt(
            **config['po_args']['state_generation']['subsequent'],
            targetAzimuth=azimuth,
            targetEllipticity=ellipticity,
            epc=epc
        )
        po.run()

    keithley = Keithley2231A(config['keithley']['address'])
    keithley.mode = DeviceMode.REMOTE
    keithley.enabled = [True, True, True]
    keithley.voltage = [5, 5, 2]


def quit():
    raise KeyboardInterrupt


processes = {
    'alignment': alignment,
    'state generation': state_generation,
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
