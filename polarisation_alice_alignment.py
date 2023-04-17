from ycqinst.keithley2231a import Keithley2231A, DeviceMode
from pOptm import PolarisationStateOptimiser
import time


dev = Keithley2231A('COM5')
dev.mode = DeviceMode.REMOTE
dev.enabled = [True, True, True]
dev.ch1.voltage = 5
dev.ch2.voltage = 2
dev.ch3.voltage = 0
del dev

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
