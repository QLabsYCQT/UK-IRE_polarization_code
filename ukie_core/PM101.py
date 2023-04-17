import pyvisa as visa
import numpy as np
import matplotlib.pyplot as plt
import time


class PM101:
    # 'USB0::0x1313::0x8078::P0035023::INSTR'):
    def __init__(self, address='USB0::0x1313::0x8076::M00806624::INSTR'):
        rm = visa.ResourceManager()
        self.pm100d = rm.open_resource(address)
        # print(self.pm100d.query("*IDN?"))
        self.powerW = 0.
        self.powerArray = []
        self.timeArray = []
        self.vis = 0.
        # self.pm100d.write("*RST;")
        return

    def power(self, averaging=1):
        """Get measured optical power"""
        self.pm100d.write('power:dc:unit W')
        p = []
        for i in range(averaging):
            p.append(float(self.pm100d.query('measure:power?')))
        self.powerW = np.mean(p)
        return self.powerW

    def monitorPower(self, tmax=1.0e9, plot=False):
        """Monitor power for tmax seconds with the option to plot live"""
        if plot:
            plt.figure(figsize=(10, 6))
            t0 = time.time()
            dt = 0.
            while dt < tmax:
                t = time.time()
                self.powerArray.append(self.power())
                dt = t - t0
                self.timeArray.append(dt)
                plt.plot(self.timeArray, self.powerArray, '-ro')
                plt.xlabel('Time (s)')
                plt.ylabel('Optical power (W)')
                plt.show()
        else:
            t0 = time.time()
            dt = 0.
            while dt < tmax:
                t = time.time()
                self.powerArray.append(self.power())
                dt = t - t0
                self.timeArray.append(dt)

    def visibility(self):
        self.vis = ((max(self.powerArray) - min(self.powerArray)) /
                    (max(self.powerArray) + min(self.powerArray)))
        return self.vis


# PM = PM100D()
# # #%%
# print(PM.power()*1e3, ' mw')
# # PM.monitorPower(tmax = 20, plot=False)

# # #%%
# # print(PM.visibility())
