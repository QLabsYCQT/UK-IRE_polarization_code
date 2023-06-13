# -*- coding: utf-8 -*-
"""
Created on Thu Oct 27 11:56:38 2022

@author: mm2921
"""

import numpy as np
import pyvisa as visa
import time


class PAX1000IR2:
    """Class to measure with the PAX1000 ThorLabs polarimeter through visa"""
    
    def __init__(self, address='USB0::0x1313::0x8031::M00844520::INSTR'):
        rm = visa.ResourceManager()
        self.polarimeter = rm.open_resource(address)
        self.data = []
        self.dataDic = {}
        self.timeseriesDic = {}
        self.time = []
        # self.polarimeter.write('*CLS')
        # self.connect()
        return
    
    def stringConversion(self, string):
        """Converts the readout string to an array of floats and then calculates 
        the values for the data dictionary"""
        data = []
        nf=0
        ni=0
        for i in string:
            if i == ',' or nf == len(string) - 1:
                number = float(string[ni:nf])
                data.append(number)
                ni = nf + 1
            nf +=1
        self.data = data 
        self.dataDic['azimuth'] = data[9] * 180 / np.pi
        self.dataDic['ellipticity'] = data[10] * 180 / np.pi
        self.dataDic['power'] = data[12]
        psi = data[9]
        chi = data[10]
        self.dataDic['S1'] = np.cos(2*psi) * np.cos(2*chi)
        self.dataDic['S2'] = np.sin(2*psi) * np.cos(2*chi)
        self.dataDic['S3'] = np.sin(2*chi)
        # print(self.dataDic)
        return
    
    def flattenDic(self):
        """Flattens the values of a dictionary into a 1d list per key."""
        def flatten(data):
            if isinstance(data, tuple):
                for x in data:
                    yield from flatten(x)
            else:
                yield data
        for k in self.timeseriesDic.keys():
            values = list(flatten(self.timeseriesDic[k]))
            self.timeseriesDic[k] = values            
        return
    
    
    def measureOnce(self):
        """Read the polarimeter dataset once"""
        self.polarimeter.write('SENS:CALC 9;:INP:ROT:STAT 1')
        dataString = self.polarimeter.query('SENS:DATA:LAT?')
        self.stringConversion(dataString)
        return self.dataDic
    
    def measureCont(self, tMeasure, tSample=1):
        """Reads the polarimeter dataset continuously for tMeasure seconds 
        every tSample seconds."""
        
        n = tMeasure / tSample
        i=0
        while i < n:
            self.measureOnce()
            keys = self.dataDic.keys()
            if i == 0:
                self.timeseriesDic = self.dataDic
                t0 = time.time()
                self.time.append(0)
            else:
                t = time.time() - t0
                values = zip(self.timeseriesDic.values(), self.dataDic.values())
                self.timeseriesDic = dict(zip(keys, values))
                self.time.append(t)
            i += 1
            time.sleep(tSample)
        
        self.flattenDic()
        self.timeseriesDic['time'] = self.time
            
        return
            
    
#%%
# a.data = []
# a.measureCont(tMeasure = 5, tSample = 1)

# #%%
# print((a.timeseriesDic)) 
# # print(a.time)
    
# #%%

# a = PAX1000IR2()
# a.measureOnce()
# print(a.dataDic)
        
        