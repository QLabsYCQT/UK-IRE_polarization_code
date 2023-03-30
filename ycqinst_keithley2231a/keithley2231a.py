import sys
homepath = 'G:/Shared drives/QComms Research/QComms Research/People/'

sys.path.append(homepath)
from HD.Python.EPCfinal.ycqinst_keithley2231a.serial_instrument import SerialInstrument
from enum import Enum
#from serial_instrument import SerialInstrument
from serial import EIGHTBITS, PARITY_NONE, STOPBITS_ONE
import logging
from time import sleep

class InvalidModeError(Exception):
    pass

class LockedChannelError(Exception):
    pass

DeviceMode = Enum('DeviceMode', ['LOCAL', 'REMOTE', 'REMOTE_LOCK'])
ChannelMode = Enum('ChannelMode', ['CONSTANT_VOLTAGE', 'CONSTANT_CURRENT'])


class VoltageIncrementor():
    def __init__(self, channel, start=None, stop=None, step=0.1, delay=1):
        self.channel = channel
        self.start = start if start is not None else channel.min_voltage
        self.stop = stop if stop is not None else channel.max_voltage
        self.step = step
        self.delay = delay
        self.channel.voltage = self.start
        while self.channel.voltage != self.start:
            pass
    
    def __iter__(self): return self

    def __next__(self):
        sleep(self.delay)
        prev = self.channel.voltage
        if prev + self.step > self.stop:
            raise StopIteration
        self.channel.voltage += self.step
        while abs(self.channel.voltage - (prev + self.step)) >= 0.01:
            pass
        return self.channel.voltage


class Channel():
    def __init__(self, device, number):
        self.device = device
        self.number = number
        self.locked = False
        self.min_voltage = 0
    
    def channel_specific(func):
        def inner(self, *args):
            if self.device.selected_channel != self.number:
                self.device._write(f'INST:NSEL {self.number}')
                self.device.selected_channel = self.number
            return func(self, *args)
        return inner
            
    
    def check_lock(self):
        if self.locked:
            raise LockedChannelError(f'Channel {self.number} is locked.')
    
    def select_channel(self):
        self.device._write(f'INST:NSEL {self.number}')
    
    @property
    @channel_specific
    def voltage(self):
        _voltage = round(float(self.device._query('FETC:VOLT?')), 2)
        return _voltage
    
    @voltage.setter
    @channel_specific
    def voltage(self, voltage):
        self.check_lock()
        self.device._write(f'VOLT {voltage}')
    
    @property
    @channel_specific
    def current(self):
        _current = round(float(self.device._query('FETC:CURR?')), 2)
        return _current
    
    @current.setter
    @channel_specific
    def current(self, current):
        self.check_lock()
        self.device._write(f'CURR {current}')
    
    @property
    @channel_specific
    def power(self):
        _power = round(float(self.device._query('FETC:POW?')), 2)
        return 

    @property
    @channel_specific
    def enabled(self):
        return bool(int(self.device._query('CHAN:OUTP?')))
    
    @enabled.setter
    @channel_specific
    def enabled(self, enabled):
        self.check_lock()
        self.device._write(f'CHAN:OUTP {int(enabled)}')
    
    @property
    @channel_specific
    def max_voltage(self):
        return float(self.device._query('VOLT? MAX'))
    
    @max_voltage.setter
    @channel_specific
    def max_voltage(self, max_voltage):
        self.device._write(f'VOLT:LIM {float(max_voltage)}')

    @property
    @channel_specific
    def max_voltage_enabled(self):
        return bool(int(self.device._query('VOLT:LIM:STAT?')))
    
    @max_voltage_enabled.setter
    @channel_specific
    def max_voltage_enabled(self, max_voltage_enabled):
        self.device._write(f'VOLT:LIM:STAT {int(max_voltage_enabled)}')


class Keithley2231A(SerialInstrument):
    def __init__(self, serial_port, log_file=None):
        port_settings = {
            'baudrate': 9600,
            'bytesize': EIGHTBITS,
            'parity': PARITY_NONE,
            'stopbits': STOPBITS_ONE,
            'timeout': 3,
            'xonxoff': False,
            'rtscts': False,
            'write_timeout': None,
            'dsrdtr': False,
            'inter_byte_timeout': None
        }
        super().__init__(serial_port, port_settings=port_settings, log_file=log_file)
        self._mode = DeviceMode.REMOTE
        self.ch1 = Channel(self, 1)
        self.ch2 = Channel(self, 2)
        self.ch3 = Channel(self, 3)
        self.channels = (self.ch1, self.ch2, self.ch3)
        self.selected_channel = None

    def test(self):
        response = self._query('*IDN?')
        print(response)

    @property
    def mode(self):
        return self._mode
    
    # @mode.setter
    # def mode(self, mode):
    #     match mode:
    #         case DeviceMode.LOCAL:
    #             self._write('SYST:LOC')
    #         case DeviceMode.REMOTE:
    #             self._write('SYST:REM')
    #         case DeviceMode.REMOTE_LOCK:
    #             self._write('SYST:RWL')
    #         case _:
    #             raise InvalidModeError(f'Invalid device mode: {mode}.')
    #     self._mode = mode
    
    @property
    def enabled(self):
        return [ch.enabled for ch in self.channels]
    
    @enabled.setter
    def enabled(self, enabled_tuple):
        for ch, enabled in zip(self.channels, enabled_tuple):
            ch.enabled = enabled
    
    @property
    def max_voltage(self):
        return [ch.max_voltage for ch in self.channels]
    
    @max_voltage.setter
    def max_voltage(self, max_voltage_tuple):
        for ch, max_voltage in zip(self.channels, max_voltage_tuple):
            ch.max_voltage = max_voltage
    
    @property
    def max_voltage_enabled(self):
        return [ch.max_voltage_enabled for ch in self.channels]
    
    @max_voltage_enabled.setter
    def max_voltage_enabled(self, max_voltage_enabled_tuple):
        for ch, max_voltage_enabled in zip(self.channels, max_voltage_enabled_tuple):
            ch.max_voltage_enabled = max_voltage_enabled

