# -*- coding: utf-8 -*-
"""
Created on Mon Jan 30 15:07:55 2023

@author: hd1242
"""


import numpy as np
import matplotlib.pyplot as plt
import sys
import time

homepath = 'G:/Shared drives/QComms Research/QComms Research/People/'

sys.path.append(homepath)

from HD.Python.EPCfinal.EPC04 import EPCdriver
#from HD.Python.EPCfinal.pm100d import PM100D
from MM.python.experiments.hardwareLibs.polarimeter.pax1000IR2 import PAX1000IR2

    
class PolarisationStateOptimiser():
    
    def __init__(self, 
                 randomV=True,
                 zeroV = False,
                 minV = False,
                 fineV=50, 
                 maxPointsSinceMax=10,
                 nEPCch=4,
                 targetAzimuth = 0.,
                 targetEllipticity = 0.,
                 angleThreshold = 0.02,
                 plot=False):
        ### Class intialization:
        self.Epc = EPCdriver( EPCAddress ='ASRL7::INSTR') #EPC address use for the state generation
        self.PolM = PAX1000IR2(address = 'USB0::0x1313::0x8031::M00920880::INSTR')

        

        
        ### Input variable definition:
        self.randomV = randomV #boolean, start from random voltages?
        self.zeroV = zeroV #boolean, start from zero voltages?
        self.minV = minV #boolean, start from -5v?
        self.targetAzimuth = targetAzimuth #target azimuth angle
        self.targetEllipticity = targetEllipticity #target ellipticity angle
        
       
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
        self.azimuthArray = []
        self.ellipticityArray = []
        self.initMaxPower = 0.
        self.power = 0.
        self.ER = 0.
        self.function = 0.
        self.erThreshold = 24.0
        self.azimuth = 0.
        self.ellipticity = 0.
        self.angleThreshold = angleThreshold

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
            
        self.PolM.measureOnce()
        self.ellipticity = self.PolM.dataDic['ellipticity']
        self.azimuth = self.PolM.dataDic['azimuth']
        self.function = np.arccos((1/2)*((np.cos((self.azimuth/360)*np.pi - (self.targetAzimuth/360)*np.pi) + 1)*np.cos((self.ellipticity/360)*np.pi - (self.targetEllipticity/360)*np.pi) + (np.cos((self.azimuth/360)*np.pi - (self.targetAzimuth/360)*np.pi) - 1)*np.cos((self.ellipticity/360)*np.pi + (self.targetEllipticity/360)*np.pi)))
        self.minF = self.function
        self.optimalV = self.initialV
        self.v = self.initialV
        
        
        #### PUT IN INIT ####
        self.gradients = []
        self.PolM.measureOnce()
        self.ellipticity = self.PolM.dataDic['ellipticity']
        self.azimuth = self.PolM.dataDic['azimuth']
        for ch in range(self.nCh):
            self.v[ch] = self.v[ch] + self.fineV
            self.Epc.setV(ch + 1, self.v[ch])
            self.PolM.measureOnce()
            self.ellipticity = self.PolM.dataDic['ellipticity']
            self.azimuth = self.PolM.dataDic['azimuth']
            f = np.arccos((1/2)*((np.cos((self.azimuth/360)*np.pi - (self.targetAzimuth/360)*np.pi) + 1)*np.cos((self.ellipticity/360)*np.pi - (self.targetEllipticity/360)*np.pi) + (np.cos((self.azimuth/360)*np.pi - (self.targetAzimuth/360)*np.pi) - 1)*np.cos((self.ellipticity/360)*np.pi + (self.targetEllipticity/360)*np.pi)))
            self.gradients.append((f - self.function) / self.fineV)
                   #self.maxPower = self.power
                   #print(self.v[ch])
        self.function = np.arccos((1/2)*((np.cos((self.azimuth/360)*np.pi - (self.targetAzimuth/360)*np.pi) + 1)*np.cos((self.ellipticity/360)*np.pi - (self.targetEllipticity/360)*np.pi) + (np.cos((self.azimuth/360)*np.pi - (self.targetAzimuth/360)*np.pi) - 1)*np.cos((self.ellipticity/360)*np.pi + (self.targetEllipticity/360)*np.pi)))
        ############################   

        print('::Initialisation complete::')
        return
    
    def gradientSearch(self):
       """Performs a gravity search algorithm to maximise contrast"""


       if self.plot:
           plt.figure()    
     
       while (self.pointsSinceMax <= self.maxPointsSinceMax):
           #print(self.gradients)
           self.ch = np.argmax(abs(np.array(self.gradients))) + 1
           vStep = self.fineV * (-1)*(np.sign(self.gradients[self.ch - 1]))
           # print('vstep',vStep)
           # print('channel',self.ch)
           # print('optimal V',self.optimalV)
           # print('min angle is,',self.minF)
           #vStep = self.fineV
           self.v[self.ch-1] = np.clip(self.v[self.ch-1] + vStep, -5000, 5000)
           #self.v[self.ch-1] = self.v[self.ch-1] + vStep
           self.Epc.setV(self.ch, int(self.v[self.ch-1]))
           time.sleep(0.1)
           self.PolM.measureOnce()
           self.ellipticity = self.PolM.dataDic['ellipticity']
           self.azimuth = self.PolM.dataDic['azimuth']
           f = np.arccos((1/2)*((np.cos((self.azimuth/360)*np.pi - (self.targetAzimuth/360)*np.pi) + 1)*np.cos((self.ellipticity/360)*np.pi - (self.targetEllipticity/360)*np.pi) + (np.cos((self.azimuth/360)*np.pi - (self.targetAzimuth/360)*np.pi) - 1)*np.cos((self.ellipticity/360)*np.pi + (self.targetEllipticity/360)*np.pi)))
           # print('pmax',p)
           # print('pmin',self.PMmin.power())
           self.gradients[self.ch - 1] = (f - self.function) / ((-1)*np.sign(self.gradients[self.ch-1])*self.fineV)
           self.function = f   
           print('angle',self.function)
           #print('gradients',self.gradients)


           if self.function < self.minF:
               #print('new max power')
               self.pointsSinceMax = 0
               self.optimalV = tuple(self.v)
               #optimalV = self.optimalV
               self.minF = self.function
               #print(self.optimalV)
               #self.Epc.setAllVoltages([int(x) for x in self.optimalV])
                
           else:
               self.pointsSinceMax += 1
               
             
               
           #if self.v[self.ch - 1] > 5000 or self.v[self.ch-1] < 5000:
               #break
           
           #self.gradients[self.ch - 1] = (self.power - self.maxPower) / self.fineV
           
           #print('new gradient',self.gradients[self.ch - 1])
           #print(self.gradients)

           
           if (all(i <= (5000 - self.fineV) for i in self.optimalV)) or( (all(i >= -5000 + self.fineV)for i in self.optimalV))is True:
               pass
           else:
               print('::Restart the algorithm::')
               break
               
           self.allPowerArray.append(self.function)
           self.azimuthArray.append(self.azimuth)
           self.ellipticityArray.append(self.ellipticity)
           
           
               
           #print('final optimal V', self.optimalV)    
           # self.Epc.setAllVoltages([int(x) for x in self.optimalV])
           
           if self.function < 0.01:
               break
           if self.pointsSinceMax > self.maxPointsSinceMax:
               print('::Algorithm too far from max::')
               break
       print('final optimal V', self.optimalV)    
       self.Epc.setAllVoltages([int(x) for x in self.optimalV])
       if self.plot:
           plt.figure()
           plt.title('angle change')
           plt.plot(self.allPowerArray,'-o')
           plt.ylabel('angle')
           plt.figure()
           plt.title('The Azimuth change')
           plt.ylabel("angle")
           plt.plot(self.azimuthArray,label = 'azimuth')
           plt.legend(loc = 'best')
           plt.figure()
           plt.title('The ellipticity change')
           plt.ylabel("angle")
           plt.plot(self.ellipticityArray,label = 'ellipticity')
           plt.legend(loc = 'best')
           #plt.plot(self.plotMaxPowerArray,'-o',color = 'red')
           #plt.plot(v1,'-o')
           #plt.plot(v2,'-o')
           #plt.plot(v3,'-o')
           #plt.legend()

       #time.sleep(0.5)    
       
       # print('===========================================================')
       # print('::Optimal voltages =  ', [int(x) for x in self.optimalV],
       #       'V::')
       
       # print('::The max power output is = ', self.maxPower, 'W::')
       
       # #print('::The voltage setting on the EPC is ', self.Epc.getVArray(),'::')
       # #time.sleep(0.2)
       # print('::The power output now is ',self.PM.power(),'::')
       
       self.Epc.setAllVoltages([int(x) for x in self.optimalV])
       self.PolM.measureOnce()
       self.ellipticity = self.PolM.dataDic['ellipticity']
       self.azimuth = self.PolM.dataDic['azimuth']
       ff = np.arccos((1/2)*((np.cos((self.azimuth/360)*np.pi - (self.targetAzimuth/360)*np.pi) + 1)*np.cos((self.ellipticity/360)*np.pi - (self.targetEllipticity/360)*np.pi) + (np.cos((self.azimuth/360)*np.pi - (self.targetAzimuth/360)*np.pi) - 1)*np.cos((self.ellipticity/360)*np.pi + (self.targetEllipticity/360)*np.pi)))
       print('::Final angle ',ff * 180,'degrees','with azimuth',self.azimuth,' and ', self.ellipticity,'::')
       
       
       
       
       return
   
    def run(self):
       """Runs the complete optimisation process"""
       self.initialisation()
       self.gradientSearch()
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
Base = PolarisationStateOptimiser(fineV = 200,
                              zeroV =False,
                              minV = False,
                          randomV = True,
                          targetAzimuth= 0,
                          targetEllipticity= 0)

Base.run()

while Base.function > Base.angleThreshold:
    Base = PolarisationStateOptimiser(fineV = 50,
                                  zeroV = False,
                                  minV = False,
                              randomV = False,
                              targetAzimuth= 0,
                              targetEllipticity=0
                              )
    Base.run()

end = time.time()

print('===========================================================')
print('Time taken to opimise the polarization is:',end - start,'s')
print('===========================================================')

Base.PolM.measureOnce()
Base.ellipticity = Base.PolM.dataDic['ellipticity']
Base.azimuth = Base.PolM.dataDic['azimuth']
#%%
print('degrees','with azimuth',Base.azimuth,' and ',Base.ellipticity,'::')
