# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 16:21:29 2023

@author: hd1242
"""
import nidaqmx
import nidaqmx.stream_readers
import numpy as np
import matplotlib.pyplot as plt
import timeit
from enum import Enum
import re
from collections import namedtuple
from time import time
from tqdm import tqdm

class koheronDetector:
    task = nidaqmx.Task('Read PD')
    ai0 = task.ai_channels.add_ai_voltage_chan('Dev1/ai0', min_val=0, max_val=5)
    ai1 = task.ai_channels.add_ai_voltage_chan('Dev1/ai1', min_val=0, max_val=5)
    task.timing.cfg_samp_clk_timing(2_000, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
    task.start()
    def __init__(self, samplingRate = 2_000):
        # name = channel.split('/')[-1]
        # self.task = nidaqmx.Task(f'Read counter {name}')
        #self.task.ai_channels.add_ai_voltage_chan(channel, min_val=0, max_val=1)
        self.task.timing.cfg_samp_clk_timing(samplingRate, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
        self.reader = nidaqmx.stream_readers.AnalogMultiChannelReader(self.task.in_stream)
        # self.task.start()
        self.powerArray = []
        self.data = []
        
        
    def getPower(self):
        # data = np.zeros(2)
        # while True:
        #     reader.read_one_sample(data)
        #     print(np.sum(data))
        #     sleep(1)
        self.data = np.zeros((2, 2000)) #input the size of array that I want
        self.reader.read_many_sample(self.data, 2000, timeout=1)
        # data_array = np.zeros((2, 32_000))
        # for i in tqdm(range(0, 1000)):
        #     reader.read_many_sample(data_array, 32_000, timeout=100)
        #     data = np.append(data, data_array, 1)
        # plt.plot(data[0,:])
        # plt.plot(data[1,:])
        # plt.show()
        # print('Aquired')
        # print(np.mean(data), np.std(data))
        # np.save('output.npy', data)
        # print('Saved')
        self.task.stop()
        #self.task.close()
        power = abs(np.mean(self.data,axis = 1))
        return power
        
# base = koheronDetector()
# #%%

# print(base.getPower())
# #%%

# base.task.close()

            
