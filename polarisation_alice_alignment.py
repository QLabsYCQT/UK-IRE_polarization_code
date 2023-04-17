# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 13:13:28 2023

@author: labuser
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import time

homepath = 'C:/Users/labuser/Documents/UK IRE Project/Python Code/EPCfinal'
sys.path.append(homepath)

from ycqinst.keithley2231a import VoltageIncrementor,Keithley2231A, DeviceMode
from EPC04 import EPCdriver
#from HD.Python.EPCfinal.pm100d import PM100D
from pax1000IR2 import PAX1000IR2
from pOptm import PolarisationStateOptimiser

dev = Keithley2231A('COM5')
dev.mode = DeviceMode.REMOTE
dev.ch1.enabled = 1
dev.ch2.enabled = 1
dev.ch3.enabled = 1
dev.ch1.voltage = 5
dev.ch2.voltage = 2
dev.ch3.voltage = 0
del dev

start = time.time()
Base = PolarisationStateOptimiser(fineV = 100,
                              zeroV = False,
                              minV = False,
                          randomV = True,
                          targetAzimuth= 45,
                          targetEllipticity= 0)

Base.run()

while Base.function > Base.angleThreshold:
    Base = PolarisationStateOptimiser(fineV = 50,
                                  zeroV = False,
                                  minV = False,
                              randomV = False,
                              targetAzimuth= 45,
                              targetEllipticity=0
                              )
    Base.run()

end = time.time()

print('===========================================================')
print('Time taken to opimise the polarization is:',end - start,'s')
print('===========================================================')

Base.PolM.measureOnce()
Base.ellipticity = Base.PolM.dataDic['ellipticity']
Base.azimuth = Base.PolM.dataDic['azimuth']

print('degrees','with azimuth',Base.azimuth,' and ellipticity',Base.ellipticity,'::')

