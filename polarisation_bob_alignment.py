# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 13:01:40 2023

@author: labuser
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import time
from ukie_core.EPC04 import EPCdriver
from ukie_core.koheronDetector import koheronDetector
from ukie_core.koheronOptimisation import PolarisationOptimiser

targetEr = float(input("Input the target extinction ratio in dB (decibel): "))
print(':::The target extinction ratio is:', targetEr, 'dB:::')

Base = PolarisationOptimiser(fineV=100,

                             zeroV=False,
                             minV=False,
                             randomV=False,

                             plot=True)

Base.run()
