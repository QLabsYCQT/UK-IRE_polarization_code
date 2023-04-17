from pOptm import PolarisationStateOptimiser
from ycqinst_keithley2231a.keithley2231a import Keithley2231A, DeviceMode

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

dev = Keithley2231A('COM5')
dev.mode = DeviceMode.REMOTE
dev.enabled = [True, True, True]
dev.ch1.voltage = 5
dev.ch2.voltage = 5
dev.ch3.voltage = 2
del dev
