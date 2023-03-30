from abc import ABC, abstractmethod
import sys
homepath = 'G:/Shared drives/QComms Research/QComms Research/People/'

sys.path.append(homepath)
from HD.Python.EPCfinal.ycqinst_keithley2231a.error_messages import *
#from error_messages import *
import logging


# TODO: use setters and getters for queries and writes 

class IEE448Instrument(ABC):
    def __init__(self, log_file = None):
        name = self.__class__.__name__
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        if not log_file:
            self.log_file = f'{name}.log'
        else:
            self.log_file = log_file
        self.handler = logging.FileHandler(self.log_file)
        self.handler.setLevel(logging.DEBUG)
        self.logger.addHandler(self.handler)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.handler.setFormatter(formatter)

    @abstractmethod
    def _query(self, message):
        pass

    @abstractmethod
    def _write(self, message):
        pass

    # Define IEEE488.2 common commands

    @property
    def idn(self) -> str:
        '''A query to identify the device; places strings of device information such as the name, firmware and version in the output queue. 

        :return: SANTEC,OTF-980,########,****.****
                 # field = serial number of the device in 8 digits.
                 * field = firmware version as 4 digits + .(period) + 4 digits.
        :rtype: str
        '''
        return self._send(r'*IDN?')

    def rst(self) -> None:
        '''Aborts standby operation. Clears command input queue and error queue.
        '''
        self._send(r'*RST')

    def tst(self) -> str:
        '''Initiates an instrument self-test and places the results in the output queue.

        :return: 0 on success, other than 0 denotes failure.  
        :rtype: str
        '''
        return self._send(r'*TST?')

    def _s_opc(self) -> None:
        '''Generates the OPC message in the Standard Event Status Register when all pending overlapped operations have been completed. 
        '''
        self._send(r'*OPC')

    def _q_opc(self) -> int:
        '''Places 1 in the output queue when all operation processing has completed. 

        :return: 0 for 'in operation', 1 for 'operation completed'.
        :rtype: int
        '''
        return self._send(r'*OPC?')

    def _s_cls(self) -> None:
        '''Clears all event registers and queues (except for the output queue) and reflects the summary in the Status Byte Register. Clears the Status Byte Register (except MAV), the Standard Event Status Register, and the error queue.
        '''
        self._send(r'*CLS')

    @property
    def ese(self, val: int) -> None:
        '''Sets the standard event enable register

        :param val: Setting value from 0 to 255
        :type val: int
        '''
        self._send(r'*ESE {}'.format(val))

    @ese.setter
    def ese(self) -> int:
        '''Places the value of the standard event enable register in the output queue.

        :return: Integer from 0 to 255
        :rtype: int
        '''
        return self._send(r'*ESE?')

    def _q_esr(self) -> int:
        '''Places the value of the standard event status register in the output queue. Register is cleared after being read. 

        :return: Integer from 0 to 255
        :rtype: int
        '''
        return self._send(r'*ESR?')


    @property
    def sre(self, val: int) -> None:
        '''Sets the service request enable register

        :param val: Integer from 0 to 255
        :type val: int
        '''
        self._send(r'*SRE {}'.format(val))

    @sre.setter
    def sre(self) -> int:
        '''Places the value of the service request enable register in the output queue.

        :return: Integer from 0 to 63, or 128 to 191
        :rtype: int
        '''
        return self._send(r'*SRE?')

    def _q_stb(self) -> int:
        '''Places the value of the status byte register in the output queue.

        :return: Integer from 0 to 255
        :rtype: int
        '''
        return self._send(r'*STB?')

    # Expose commands with more user-friendly names. Where commands can be
    # used both for setting and querying, a more complex function is
    # exposed which decides which action to perform depending on the
    # presence of a parameter - no parameter means query, one parameter
    # means set, and more parameters throws an error.

    # Set short aliases for IEEE488.2 common commands
    cls = _s_cls
    esr = _q_esr
    stb = _q_stb

    def opc(self, *args) -> None:
        '''(0 args): 

        :raises TypeError: When more than 1 argument given
        :return: _description_
        :rtype: _type_
        '''
        if len(args) == 0:
            return self._q_opc()
        elif len(args) == 1:
            self._s_opc()
        else:
            raise TypeError(args_msg)

    def ese(self, *args) -> int or None:
        if len(args) == 0:
            return self._q_ese()
        elif len(args) == 1:
            if args[0] not in [i for i in range(0, 256)]:
                raise ValueError(eight_bit_val_msg)
            self._s_ese(args[0])
        else:
            raise TypeError(args_msg)

    def sre(self, *args) -> int or None:
        if len(args) == 0:
            return self._q_sre
        elif len(args) == 1:
            if args[0] not in [i for i in range(0, 256)]:
                raise ValueError(eight_bit_val_msg)
            self._s_sre(args[0])
        else:
            raise TypeError(args_msg)

    # Set long aliases for IEEE488.2 common commands
    identify = idn
    reset = rst
    self_test = tst
    operation_complete = opc
    status_clear = cls
    standard_event_enable_register = ese
    standard_event_status_register = esr
    service_request_enable = sre
    status_byte_register = stb