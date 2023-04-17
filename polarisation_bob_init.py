# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 15:17:55 2023

@author: labuser
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import time
# from time import sleep
# import nidaqmx
# import nidaqmx.stream_readers
# import numpy as np
# import matplotlib.pyplot as plt
#2 import timeit
# from enum import Enum
# import re
# from collections import namedtuple
# from time import time
# from tqdm import tqdm

homepath = 'C:/Users/labuser/Documents/UK-IRE project/Python Code'

sys.path.append(homepath)

from EPCfinal.EPC04 import EPCdriver
#from HD.Python.EPCfinal.pm100d import PM100D
from EPCfinal.koheronDetector import koheronDetector
from EPCfinal.keheronOptimisation import PolarisationOptimiser
import idqube

qube = idqube.IDQube("COM4")
qubeMin = idqube.IDQube("COM5")

qube.set_detector_eff_temp_indexes(1,1)
qubeMin.set_detector_eff_temp_indexes(1,1)

time.sleep(3)
print('The detection efficiency for Q1 is',qube.detector_efficiency)
print('The detection efficiency for Q2 is',qubeMin.detector_efficiency)
EPC = EPCdriver(EPCAddress ='ASRL3::INSTR')
EPC.setDC()
print('working mode for the EPC is',EPC.getmode())
