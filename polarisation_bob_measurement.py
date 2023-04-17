import idqube
import numpy as np
import time


qube = idqube.IDQube("COM4")
qubeMin = idqube.IDQube("COM5")

qube.set_detector_eff_temp_indexes(4, 1)
qubeMin.set_detector_eff_temp_indexes(4, 1)
time.sleep(3)

print('Initial count for Q1', qube.photon_count)
print('Initial count for Q2', qubeMin.photon_count)

qubeArray = []
qubeMinArray = []
ER = []
start = time.time()
end = time.time()
while (end - start) < 600:
    qubeArray.append(qube.photon_count)
    qubeMinArray.append(qubeMin.photon_count)
    ER.append(10 * np.log(qube.photon_count / qube.photon_count))
    end = time.time()
print('::Finish::')

filename = input('Input a (safe) filename for output data')
np.savetxt(filename, ((qubeArray), (qubeMinArray)), delimiter=',')
