# -*- coding: utf-8 -*-
"""
Created on Wed Feb 22 14:52:08 2023

@author: hd1242
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

homepath = 'G:/Shared drives/QComms Research/QComms Research/People/'

sys.path.append(homepath)

from HD.Python.EPCfinal.EPC04 import EPCdriver
#from HD.Python.EPCfinal.pm100d import PM100D
from HD.Python.EPCfinal.koheronDetector import koheronDetector

    
class PolarisationOptimiser():
    
    def __init__(self, 
                 randomV=True,
                 zeroV = False,
                 minV = False,
                 fineV=50, 
                 maxPointsSinceMax=10,
                 nEPCch=4,
                 erThreshold = 29,
                 plot=False):
        ### Class intialization:
        self.Epc = EPCdriver(EPCAddress ='ASRL3::INSTR')
        self.PM = koheronDetector()
        
        

        
        ### Input variable definition:
        self.randomV = randomV #boolean, start from random voltages?
        self.zeroV = zeroV #boolean, start from zero voltages?
        self.minV = minV #boolean, start from -5v?
        
       
        self.fineV = fineV #V, fine voltage steps
        
        self.maxPointsSinceMax = maxPointsSinceMax
        self.nCh = nEPCch #int, number of EPC channels to use
        self.plot = plot #boolean, plot contrast online?

    
        
        
        ### Variable initialisation:
        self.initialV = [] #array of initial voltages
        self.optimalV = [] #array of optimal voltages
        self.gradients = [] #array of gradients
        self.v = []
        self.pointsSinceMax = 0 #number of points since last max contrast
        self.maxPower = 0. #current powermeter reading
        self.allPowerArray = [] #all contrasts
        self.plotMaxPowerArray = []
        self.absgradients = []
        self.erArray = []
        self.initMaxPower = 0.
        self.power = 0.
        self.ER = 0.
        self.erThreshold = erThreshold

        pass
    
    
    def initialisation(self):
        """initialises the optimisation from 
        random or set EPC voltages"""
        
        
        if self.randomV:
            self.Epc.randomiseV()
            self.initialV = self.Epc.getVArray()
            
        elif self.zeroV:
            self.Epc.intV()
            self.initialV = self.Epc.getVArray()
            
                
        elif self.minV:
            self.Epc.setMinVoltage()
            self.initialV= self.Epc.getVArray()

        else:
            self.initialV = self.Epc.getVArray()
            
        self.power = abs(self.PM.getPower()[0])
        self.maxPower = self.power
        self.optimalV = self.initialV
        self.v = self.initialV
        
        
        #### PUT IN INIT ####
        self.gradients = []
        for ch in range(self.nCh):
            self.v[ch] = self.v[ch] + self.fineV
            self.Epc.setV(ch + 1, self.v[ch])
            p = abs(self.PM.getPower()[0])
            self.gradients.append((p - self.power) / self.fineV)
                   #self.maxPower = self.power
            # print(self.v[ch])
            # print(p)
        self.power = abs(self.PM.getPower()[0])
        #print('intialisation power', self.power)
        ############################   

        print('::Initialisation complete::')
        return
    
    def gradientSearch(self):
       """Performs a gravity search algorithm to maximise contrast"""
       
       v1 = []
       v2 = []
       v3 = []

       if self.plot:
           plt.figure()    
     
       while (self.pointsSinceMax <= self.maxPointsSinceMax) and (self.ER < self.erThreshold):
           # print(self.gradients)
           # print('points since max', self.pointsSinceMax)
           self.ch = np.argmax(abs(np.array(self.gradients))) + 1
           vStep = self.fineV * (np.sign(self.gradients[self.ch - 1]))
           #vStep = self.fineV
           # print('vstep', vStep)
           self.v[self.ch-1] = np.clip(self.v[self.ch-1] + vStep, -5000, 5000)
           #self.v[self.ch-1] = self.v[self.ch-1] + vStep
           self.Epc.setV(self.ch, int(self.v[self.ch-1]))
           p = abs(self.PM.getPower()[0])
           # print('pmax',p)
           # print('pmin',self.PMmin.power())
           self.ER = 10 * np.log10(p / abs(self.PM.getPower()[1]))
           self.erArray.append(self.ER)
           self.gradients[self.ch - 1] = (p - abs(self.power)) / (np.sign(self.gradients[self.ch-1])*self.fineV)
           self.power = p
           # print('optimal V',self.optimalV)
           print('extinction ratio',self.ER)
           # print('max power',self.power)
           # print('gradient',self.gradients)
           
           v1.append(self.v[0])
           v2.append(self.v[1])
           v3.append(self.v[2])
           
           if self.power > self.maxPower:
               # print('new max power',p)
               self.pointsSinceMax = 0
               self.optimalV = tuple(self.v)
               self.maxPower = self.power
               self.Epc.setAllVoltages([int(x) for x in self.optimalV])
                
           else:
               self.pointsSinceMax += 1
               
               
           if self.ER > 20:
               self.fineV = 100
               if self.ER > 24:
                   self.fineV = 50
                
               
             
               
           #if self.v[self.ch - 1] > 5000 or self.v[self.ch-1] < 5000:
               #break
           
           #self.gradients[self.ch - 1] = (self.power - self.maxPower) / self.fineV
           
           #print('new gradient',self.gradients[self.ch - 1])
           #print(self.gradients)

           self.allPowerArray.append(self.power)
           self.plotMaxPowerArray.append(self.power * 300000)
           
           if (all(i <= (5000 - self.fineV) for i in self.optimalV)) or( (all(i >= -5000 + self.fineV)for i in self.optimalV))is True:
               pass
           else:
               print('::Restart the algorithm::')
               break
               
               
           if self.plot:
               plt.plot(self.allPowerArray,'-o')
               #plt.plot(self.plotMaxPowerArray,'-o',color = 'red')
               #plt.plot(v1,'-o')
               #plt.plot(v2,'-o')
               #plt.plot(v3,'-o')
               #plt.legend()
               
               
           self.Epc.setAllVoltages([int(x) for x in self.optimalV])
           
           
           if self.pointsSinceMax > self.maxPointsSinceMax:
               print('::Algorithm too far from max::')
               break
           
            

       #time.sleep(0.5)    
       
       # print('===========================================================')
       # print('::Optimal voltages =  ', [int(x) for x in self.optimalV],
       #       'V::')
       
       # print('::The max power output is = ', self.maxPower, 'W::')
       
       # #print('::The voltage setting on the EPC is ', self.Epc.getVArray(),'::')
       # #time.sleep(0.2)
       # print('::The power output now is ',self.PM.power(),'::')
       
       self.ER = 10*np.log10(self.PM.getPower()[0]/abs(self.PM.getPower()[1]))
       
       print('::The corresponding extinction ration is ',self.ER,'::' ,self.PM.getPower()[0],self.PM.getPower()[1])
       
       
       
       
       return
   
    def run(self):
       """Runs the complete optimisation process"""
       self.initialisation()
       self.gradientSearch()
       self.PM.task.close()
       '''
       self.initialisation(zeroV = False,
                         randomV = False,
                            minV = False)
       while self.ER < self.erThreshold:
           self.gradientSearch()
       '''
      
           
       return
#%%
start = time.time()
Base = PolarisationOptimiser(fineV = 100,
                             randomV = False,
                              zeroV = False,
                              minV = False,                         
                          plot = False)

Base.run()

# Base.zeroV = False
# Base.initialisation()
# while Base.ER < Base.erThreshold:
     # Base = PolarisationOptimiser(fineV = 50,
     #                               zeroV = False,
     #                               minV = False,
     #                           randomV = False,
     #                           plot = True)

     # Base.run()
end = time.time()



print('===========================================================')
print('Time taken to opimise the polarization is:',end - start,'s')
print('===========================================================')
