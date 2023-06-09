from abc import ABC, abstractmethod
from enum import Enum
import numpy as np
from .pax1000IR2 import PAX1000IR2
from .koheronDetector import koheronDetector
from yqcinst.instruments.epc04 import EPC04
import random
from time import sleep


def convert_angle(thorlabs_angle):
    poincare_angle = np.pi * thorlabs_angle / 360
    return poincare_angle


def index_of_abs_max(ls: list):
    ls = [abs(i) for i in ls]
    return ls.index(max(ls))


InitMode = Enum('InitMode', ['RANDOM_V', 'ZERO_V', 'MIN_V'])


class PolarisationOptimiser(ABC):

    def __init__(self,
                 mode=InitMode.RANDOM_V,
                 coarse_voltage_step=100,
                 fine_voltage_step=50,
                 max_steps_since_local_min=10,
                 epc: EPC04 = None,
                 epc_channel_count=4,
                 cf_threshold=0
                 ):
        self.mode = mode
        self.coarse_voltage_step = coarse_voltage_step
        self.fine_voltage_step = fine_voltage_step
        self.max_steps_since_local_min = max_steps_since_local_min
        self.epc = epc
        self.epc_channel_count = epc_channel_count
        self.cf_threshold = cf_threshold
        self.data = np.zeros((1, self.epc_channel_count + 1))

    def gradient_search(self):
        steps_since_local_min = 0

        while (steps_since_local_min <= self.max_steps_since_local_min):
            active_channel = index_of_abs_max(self.gradients)
            voltage_step = (
                self.voltage_step *
                -1 *
                np.sign(self.gradients[active_channel])
            )
            self.current_voltages[active_channel] += voltage_step
            self.epc.channels[active_channel].voltage = self.current_voltages[active_channel]
            sleep(0.1)
            cf = self.cost_function()
            self.gradients[active_channel] = (
                (cf - self.current_cf) / voltage_step
            )
            self.current_cf = cf
            self.data = np.append(
                self.data,
                self.current_voltages + [self.current_cf],
                axis=0
            )

            if self.current_cf < self.min_cf:
                steps_since_local_min = 0
                self.min_cf = self.current_cf
            else:
                steps_since_local_min += 1
            
            if self.current_cf < 10 * self.cf_threshold:
                self.voltage_step = self.fine_voltage_step
            else:
                self.voltage_step = self.coarse_voltage_step
            
            if self.current_cf < self.cf_threshold:
                break

            if steps_since_local_min == self.max_steps_since_local_min:
                self.initialisation()
                steps_since_local_min = 0
            
            if np.max(self.current_voltages) > 4500:
                self.initialisation()

    @abstractmethod
    def cost_function(self):
        pass

    def initialisation(self):
        if self.mode is InitMode.RANDOM_V:
            self.initial_voltages = [
                int((random.random() - 0.5) * 10000) for _ in range(4)
            ]
        elif self.mode is InitMode.ZERO_V:
            self.initial_voltages = [0 for _ in range(4)]
        elif self.mode is InitMode.MIN_V:
            self.initial_voltages = [-5000 for _ in range(4)]
        self.epc.voltages = self.initial_voltages

        self.current_cf = self.cost_function()        
        self.optimal_voltages = self.initial_voltages
        self.current_voltages = self.initial_voltages

        self.gradients = [0 for _ in range(self.epc_channel_count)]
        for i, ch in enumerate(self.epc.channels):
            ch.voltage = self.current_voltages[i] + self.voltage_step
            sleep(0.05)
            cf = self.cost_function()
            self.gradients[i] = (cf - self.current_cf) / self.voltage_step
            self.current_cf = cf
        print(self.gradients)
        self.data = np.array(
            self.current_voltages + [self.current_cf]
        )
        self.min_cf = self.current_cf


class KoheronPolarisationOptimiser(PolarisationOptimiser):
    def __init__(self,
                 cf_threshold,
                 target_channel=0,
                 detector: koheronDetector,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.target_er = target_er
        self.detector = detector

    def cost_function(self):
        return -1 * self.detector.getPower()[target_channel]


class PAX1000IR2PolarisationOptimiser(PolarisationOptimiser):

    def __init__(self,
                 target_azimuth,
                 target_ellipticity,
                 polarimeter: PAX1000IR2,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.target_azimuth = convert_angle(target_azimuth)
        self.target_ellipticity = convert_angle(target_ellipticity)
        self.polarimeter = polarimeter

    def cost_function(self):
        self.polarimeter.measureOnce()
        azimuth = convert_angle(self.polarimeter.dataDic['azimuth'])
        ellipticity = convert_angle(self.polarimeter.dataDic['ellipticity'])
        return np.arccos(
            0.5 * (
                (
                    np.cos(
                        azimuth -
                        self.target_azimuth
                    ) + 1
                ) * (
                    np.cos(
                        ellipticity -
                        self.target_ellipticity
                    )
                ) + (
                    np.cos(
                        azimuth -
                        self.target_azimuth
                    ) - 1
                ) * (
                    np.cos(
                        ellipticity +
                        self.target_ellipticity
                    )
                )
            )
        )
