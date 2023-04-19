from ukie_core.PM101 import PolarisationOptimiser
from ukie_core.EPC04 import EPCdriver
import idqube
import time
import numpy as np


def init(config):
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


def alignment(config):
    targetEr = float(
        input("Input the target extinction ratio in dB (decibel): "))
    print(':::The target extinction ratio is:', targetEr, 'dB:::')

    Base = PolarisationOptimiser(fineV=100,
                                 zeroV=False,
                                 minV=False,
                                 randomV=False,
                                 plot=True)

    Base.run()


def measurement(config):
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
