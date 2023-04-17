import time
from ukie_core.EPC04 import EPCdriver
import idqube

qube = idqube.IDQube("COM4")
qubeMin = idqube.IDQube("COM5")

qube.set_detector_eff_temp_indexes(1, 1)
qubeMin.set_detector_eff_temp_indexes(1, 1)

time.sleep(3)
print('The detection efficiency for Q1 is', qube.detector_efficiency)
print('The detection efficiency for Q2 is', qubeMin.detector_efficiency)
EPC = EPCdriver(EPCAddress='ASRL3::INSTR')
EPC.setDC()
print('working mode for the EPC is', EPC.getmode())
