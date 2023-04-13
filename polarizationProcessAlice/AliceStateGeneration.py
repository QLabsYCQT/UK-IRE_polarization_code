# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 13:17:23 2023

@author: labuser
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import time

homepath = 'C:/Users/labuser/Documents/UK IRE Project/Python Code/EPCfinal'
sys.path.append(homepath)

from EPC04 import EPCdriver
#from HD.Python.EPCfinal.pm100d import PM100D
from pax1000IR2 import PAX1000IR2
from pOptm import PolarisationStateOptimiser
from ycqinst.keithley2231a import VoltageIncrementor,Keithley2231A, DeviceMode

azimuth = int(input("Input the target azimuth angle in degrees: (-90 < angle < 90) "))
ellipticity = int(input("Input the target ellipticity angle in degrees: (-45 < angle < 45) "))
print(':::The target azimuth angle is:', azimuth,'degrees:::')
print(':::The target ellipticity angle is:', ellipticity,'degrees:::')
# azimuth = 0
# ellipticity = 0
Base = PolarisationStateOptimiser(fineV = 100,
                              zeroV = False,
                              minV = False,
                          randomV = False,
                          targetAzimuth= azimuth,
                          targetEllipticity= ellipticity
                          
                          )

Base.run()

while Base.function > Base.angleThreshold:
    Base = PolarisationStateOptimiser(fineV = 50,
                                  zeroV = False,
                                  minV = False,
                              randomV = False,
                              targetAzimuth= azimuth,
                              targetEllipticity= ellipticity
                              )
    Base.run()
    
dev = Keithley2231A('COM5')
dev.mode = DeviceMode.REMOTE
dev.ch1.enabled = 1
dev.ch2.enabled = 1
dev.ch3.enabled = 1
dev.ch1.voltage = 5
dev.ch2.voltage = 5
dev.ch3.voltage = 2
del dev