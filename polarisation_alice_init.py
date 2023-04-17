from EPC04 import EPCdriver
from ycqinst.keithley2231a import Keithley2231A, DeviceMode

EPC = EPCdriver(EPCAddress='ASRL3::INSTR')
EPC.setDC()

dev = Keithley2231A('COM5')
dev.mode = DeviceMode.REMOTE
dev.enabled = [True, True, True]
dev.ch1.voltage = 5
dev.ch2.voltage = 5
dev.ch3.voltage = 5
del dev
