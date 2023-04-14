# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 15:12:11 2023

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
EPC = EPCdriver( EPCAddress ='ASRL3::INSTR')
dev = Keithley2231A('COM5')
dev.mode = DeviceMode.REMOTE
dev.ch1.enabled = 1
dev.ch2.enabled = 1
dev.ch3.enabled = 1
dev.ch1.voltage = 5
dev.ch2.voltage = 5
dev.ch3.voltage = 5
del dev

EPC.setDC()
print(EPC.getmode())