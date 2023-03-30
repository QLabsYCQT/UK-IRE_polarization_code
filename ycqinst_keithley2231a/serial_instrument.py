import serial
import sys
homepath = 'G:/Shared drives/QComms Research/QComms Research/People/'

sys.path.append(homepath)
from HD.Python.EPCfinal.ycqinst_keithley2231a.ieee448_instrument import IEE448Instrument
#from ieee448_instrument import IEE448Instrument
from time import sleep
import re


class SerialInstrument(IEE448Instrument):
    def __init__(self, serial_port, port_settings = {}, termination_character = '\n', log_file=None):
        super().__init__(log_file=log_file)
        self.serial_port = serial.Serial(**port_settings)
        self.serial_port.port = serial_port
        self.termination_character = termination_character
    
    
    def _query(self, message):
        self.serial_port.open()
        self.serial_port.write((message + self.termination_character).encode('utf-8'))
        response = self.serial_port.readline().decode('utf-8')
        if response:
            self.logger.info(f'Query: {message}; Response: {response[:-1]}')
        else:
            self.logger.warn(f'Query: {message}; Received no response before timeout.')
            return None
        self.serial_port.close()
        if re.search('[^0-9]', response) is None:
            response = int(response)
        elif re.search('[^0-9.]', response) is None:
            response = float(response)
        else:
            response = str(response)
        return response
    
    def _write(self, message):
        self.serial_port.open()
        self.serial_port.write((message + self.termination_character).encode('utf-8'))
        self.logger.info(f'Write: {message}')
        self.serial_port.close()

    @property
    def port_is_open(self):
        return self.serial_port.is_open
    

