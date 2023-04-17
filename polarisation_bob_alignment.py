# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 13:01:40 2023

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
# import timeit
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

targetEr = float(input("Input the target extinction ratio in dB (decibel): "))
print(':::The target extinction ratio is:', targetEr,'dB:::') 

Base = PolarisationOptimiser(fineV = 100,
                            
                              zeroV = False,
                              minV = False,
                          randomV = False,
                          
                          plot = True)

Base.run()