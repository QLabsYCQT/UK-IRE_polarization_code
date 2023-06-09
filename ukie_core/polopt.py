from abc import ABC, abstractmethod
from enum import Enum
import numpy as np
from .pax1000IR2 import PAX1000IR2
from .koheronDetector import koheronDetector
from yqcinst.instruments.epc04 import EPC04
import random


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
                 voltage_step_size=50,
                 max_steps_since_local_max=10,
                 epc: EPC04 = None,
                 epc_channel_count=4
                 ):
        self.mode = mode
        self.voltage_step_size = voltage_step_size
        self.max_steps_since_local_max = max_steps_since_local_max
        self.epc = epc
        self.epc_channel_count = epc_channel_count
        self.data = np.zeros((1, self.epc_channel_count + 1))

    def gradient_search(self):
        steps_since_local_max = 0
        too_far_from_local_max = \
            steps_since_local_max <= self.max_steps_since_local_max

        while not too_far_from_local_max:
            active_channel = index_of_abs_max(self.gradients)
            voltage_step = (
                self.voltage_step_size *
                -1 *
                np.sign(self.gradients[active_channel])
            )
            self.epc.channels[active_channel + 1].voltage += voltage_step
            cf = self.cost_function()
            self.gradients[active_channel] = (
                cf - self.current_cf / voltage_step
            )
            self.current_cf = cf
            self.data = np.append(
                self.data,
                list(self.current_voltages).append(self.current_cf),
                axis=0
            )

            if self.current_cf > self.max_cf:
                steps_since_local_max = 0
                self.max_cf = self.current_cf
            else:
                steps_since_local_max += 1

            if steps_since_local_max > self.max_steps_since_local_max:
                break

    @abstractmethod
    def cost_function(self):
        pass

    def initialisation(self):
        if self.mode is InitMode.RANDOM_V:
            self.epc.voltages = [
                int((random.random() - 0.5) * 10000) for _ in range(4)
            ]
        elif self.mode is InitMode.ZERO_V:
            self.epc.voltages = [0 for _ in range(4)]
        elif self.mode is InitMode.MIN_V:
            self.epc.voltages = [-5000 for _ in range(4)]
        self.initial_voltages = self.epc.voltages

        self.max_cf = self.cost_function()
        self.current_cf = self.cost_function()
        self.optimal_voltages = self.initial_voltages
        self.current_voltages = self.initial_voltages

        self.gradients = [0 for _ in range(self.epc_channel_count)]
        for i, ch in enumerate(self.epc.channels):
            ch.voltage += self.voltage_step
            cf = self.cost_function()
            self.gradients[i] = (cf - self.max_cf) / self.voltage_step
        self.data = np.array(
            list(self.current_voltages).append(self.current_cf)
        )


class KoheronPolarisationOptimiser(PolarisationOptimiser):
    def __init__(self,
                 target_er,
                 detector: koheronDetector,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.target_er = target_er
        self.detector = detector

    def cost_function(self):
        return self.detector.getPower()


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
