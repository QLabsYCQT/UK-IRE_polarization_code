import numpy as np
import matplotlib.pyplot as plt

from .EPC04 import EPCDriver
from .koheronDetector import koheronDetector


class PolarisationOptimiser():

    def __init__(self,
                 randomV=True,
                 zeroV=False,
                 minV=False,
                 fineV=50,
                 maxPointsSinceMax=10,
                 nEPCch=4,
                 erThreshold=29,
                 plot=False,
                 epc=None,
                 pm=None):

        # Class intialization:
        if epc is None:
            self.epc = EPCDriver(EPCAddress='ASRL3::INSTR')

        if pm is None:
            self.PM = koheronDetector()

        # Input variable definition:
        self.randomV = randomV  # boolean, start from random voltages?
        self.zeroV = zeroV  # boolean, start from zero voltages?
        self.minV = minV  # boolean, start from -5v?

        self.fineV = fineV  # V, fine voltage steps

        self.maxPointsSinceMax = maxPointsSinceMax
        self.nCh = nEPCch  # int, number of EPC channels to use
        self.plot = plot  # boolean, plot contrast online?

        # Variable initialisation:
        self.initialV = []  # array of initial voltages
        self.optimalV = []  # array of optimal voltages
        self.gradients = []  # array of gradients
        self.v = []
        self.pointsSinceMax = 0  # number of points since last max contrast
        self.maxPower = 0.  # current powermeter reading
        self.allPowerArray = []  # all contrasts
        self.plotMaxPowerArray = []
        self.absgradients = []
        self.erArray = []
        self.initMaxPower = 0.
        self.power = 0.
        self.extinction_ratio = 0.
        self.erThreshold = erThreshold

    def initialisation(self):
        """initialises the optimisation from
        random or set EPC voltages"""

        if self.randomV:
            self.epc.randomiseV()
            self.initialV = self.epc.getVArray()

        elif self.zeroV:
            self.epc.intV()
            self.initialV = self.epc.getVArray()

        elif self.minV:
            self.epc.setMinVoltage()
            self.initialV = self.epc.getVArray()

        else:
            self.initialV = self.epc.getVArray()

        self.power = abs(self.PM.getPower()[0])
        self.maxPower = self.power
        self.optimalV = self.initialV
        self.v = self.initialV

        #### PUT IN INIT ####
        self.gradients = []
        for ch in range(self.nCh):
            self.v[ch] = self.v[ch] + self.fineV
            self.epc.setV(ch + 1, self.v[ch])
            p = abs(self.PM.getPower()[0])
            self.gradients.append((p - self.power) / self.fineV)
        self.power = abs(self.PM.getPower()[0])
        ############################

        print('::Initialisation complete::')

    def gradientSearch(self):
        """Performs a gravity search algorithm to maximise contrast"""

        v1 = []
        v2 = []
        v3 = []

        if self.plot:
            plt.figure()

        while (self.pointsSinceMax <= self.maxPointsSinceMax) and (self.extinction_ratio < self.erThreshold):
            self.ch = np.argmax(abs(np.array(self.gradients))) + 1
            vStep = self.fineV * (np.sign(self.gradients[self.ch - 1]))
            self.v[self.ch-1] = np.clip(self.v[self.ch-1] + vStep, -5000, 5000)
            self.epc.setV(self.ch, int(self.v[self.ch-1]))
            p = abs(self.PM.getPower()[0])
            self.extinction_ratio = 10 * \
                np.log10(p / abs(self.PM.getPower()[1]))
            self.erArray.append(self.extinction_ratio)
            self.gradients[self.ch - 1] = (p - abs(self.power)) / \
                (np.sign(self.gradients[self.ch-1])*self.fineV)
            self.power = p
            print('extinction ratio', self.extinction_ratio)

            v1.append(self.v[0])
            v2.append(self.v[1])
            v3.append(self.v[2])

            if self.power > self.maxPower:
                self.pointsSinceMax = 0
                self.optimalV = tuple(self.v)
                self.maxPower = self.power
                self.epc.setAllVoltages([int(x) for x in self.optimalV])

            else:
                self.pointsSinceMax += 1

            if self.extinction_ratio > 20:
                self.fineV = 100
                if self.extinction_ratio > 24:
                    self.fineV = 50

            self.allPowerArray.append(self.power)
            self.plotMaxPowerArray.append(self.power * 300000)

            if (all(i <= (5000 - self.fineV) for i in self.optimalV)) or ((all(i >= -5000 + self.fineV)for i in self.optimalV)) is True:
                pass
            else:
                print('::Restart the algorithm::')
                break

            if self.plot:
                plt.plot(self.allPowerArray, '-o')

            self.epc.setAllVoltages([int(x) for x in self.optimalV])

            if self.pointsSinceMax > self.maxPointsSinceMax:
                print('::Algorithm too far from max::')
                break

        self.extinction_ratio = 10 * \
            np.log10(self.PM.getPower()[0]/abs(self.PM.getPower()[1]))

        print('::The corresponding extinction ration is ', self.extinction_ratio,
              '::', self.PM.getPower()[0], self.PM.getPower()[1])

    def run(self):
        """Runs the complete optimisation process"""
        self.initialisation()
