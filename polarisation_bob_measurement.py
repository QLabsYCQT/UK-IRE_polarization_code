# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 13:20:21 2023

@author: labuser
"""
import idqube
import numpy as np
import time
import matplotlib.pyplot as plt
qube = idqube.IDQube("COM4")
qubeMin = idqube.IDQube("COM5")

qube.set_detector_eff_temp_indexes(4,1)
qubeMin.set_detector_eff_temp_indexes(4,1)
time.sleep(3)

print('Initial count for Q1',qube. photon_count)
print('Initial count for Q2',qubeMin. photon_count)
qubeArray = []
qubeMinArray = []
ER = []
start = time.time()
end = time.time()
while (end - start) < 600:
    
    qubeArray.append(qube. photon_count)
    # time.sleep(0.5)
    qubeMinArray.append(qubeMin. photon_count)
    ER.append(10*np.log(qube. photon_count/qube. photon_count))
    end = time.time()
# len(qubeArray)
print('::Finish::')

np.savetxt('QBER IDQubes drift after optimisation V state March 05 align diagonal.csv', ((qubeArray), (qubeMinArray)), delimiter=',')
