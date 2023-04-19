from ukie_core.EPC04 import EPCdriver
from ukie_core.PM101 import PolarisationStateOptimiser
from ycqinst.instruments.keithley2231a import Keithley2231A, DeviceMode
import time


def init(config):
    EPC = EPCdriver(config['epc']['address'])
    EPC.setDC()

    keithley = Keithley2231A(config['keithley']['address'])
    keithley.mode = DeviceMode.REMOTE
    keithley.enabled = [True, True, True]
    keithley.voltage = [5, 5, 5]
    config['keithley']['device_handle'] = keithley


def alignment(config):
    keithley = config['keithley']['device_handle']
    keithley.voltage = [5, 2, 0]

    start = time.time()
    Base = PolarisationStateOptimiser(fineV=100,
                                      zeroV=False,
                                      minV=False,
                                      randomV=True,
                                      targetAzimuth=45,
                                      targetEllipticity=0)

    Base.run()

    while Base.function > Base.angleThreshold:
        Base = PolarisationStateOptimiser(fineV=50,
                                          zeroV=False,
                                          minV=False,
                                          randomV=False,
                                          targetAzimuth=45,
                                          targetEllipticity=0)
        Base.run()

    end = time.time()

    print('===========================================================')
    print('Time taken to opimise the polarization is:', end - start, 's')
    print('===========================================================')

    Base.PolM.measureOnce()
    Base.ellipticity = Base.PolM.dataDic['ellipticity']
    Base.azimuth = Base.PolM.dataDic['azimuth']

    print('degrees', 'with azimuth', Base.azimuth,
          ' and ellipticity', Base.ellipticity, '::')


def state_generation(config):
    azimuth = int(
        input("Input the target azimuth angle in degrees: (-90 < angle < 90) "))
    ellipticity = int(
        input("Input the target ellipticity angle in degrees: (-45 < angle < 45) "))
    print(':::The target azimuth angle is:', azimuth, 'degrees:::')
    print(':::The target ellipticity angle is:', ellipticity, 'degrees:::')

    Base = PolarisationStateOptimiser(fineV=100,
                                      zeroV=False,
                                      minV=False,
                                      randomV=False,
                                      targetAzimuth=azimuth,
                                      targetEllipticity=ellipticity)

    Base.run()

    while Base.function > Base.angleThreshold:
        Base = PolarisationStateOptimiser(fineV=50,
                                          zeroV=False,
                                          minV=False,
                                          randomV=False,
                                          targetAzimuth=azimuth,
                                          targetEllipticity=ellipticity)
        Base.run()

    keithley = config['keithley']['device_handle']
    keithley.voltage = [5, 5, 2]
