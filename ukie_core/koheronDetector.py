import nidaqmx
import nidaqmx.stream_readers
import numpy as np


class koheronDetector:

    def __init__(self, samplingRate=2_000):
        self.task = nidaqmx.Task('Read PD')
        self.ai0 = self.task.ai_channels.add_ai_voltage_chan(
            'Dev1/ai0',
            min_val=0,
            max_val=5)
        self.ai1 = self.task.ai_channels.add_ai_voltage_chan(
            'Dev1/ai1',
            min_val=0,
            max_val=5)
        self.task.timing.cfg_samp_clk_timing(
            2_000,
            sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
        self.task.timing.cfg_samp_clk_timing(
            samplingRate,
            sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
        self.reader = nidaqmx.stream_readers.AnalogMultiChannelReader(
            self.task.in_stream)
        self.powerArray = []
        self.data = []
        self.task.start()

    def getPower(self):
        self.data = np.zeros((2, 2000))  # input the size of array that I want
        self.reader.read_many_sample(self.data, 2000, timeout=1)
        self.task.stop()
        power = abs(np.mean(self.data, axis=1))
        return power
