import pyvisa as visa
import time
import random


class EPCDriver:

    voltage_lim = (-5., 5.)
    frequency_lim = (0, 100)

    """
    This will control the function of the electric polarization controller
    """

    def __init__(self, address='ASRL3::INSTR'):
        """
        This will initialize visa and connect to the device (EPC).

        Args:
            EPC_address (str): Address of the device. ''.
        """

        rm = visa.ResourceManager()

        self.epc = rm.open_resource(address)
        self.epc.write_termination = '\r\n'
        self.epc.read_termination = '\r\n'

    def _parse_response(self, comm, resp):
        resp = [s.strip() for s in resp.splitlines() if s.strip()]
        if resp and (resp[0] == comm):
            resp = resp[1:]

        resp = resp[:-1]
        return resp

    def flush_read(self):
        """Flush the device output (read all the available data; return the number of bytes read)"""
        return len(self.read())

    def getmode(self):
        """
        This function will tell us the mode (AC/DC) of the device that is opearting.
        """
        self.epc.flush(64)
        mode = self.epc.query('M?')

        return mode

    def setAC(self):
        """
        This function will change the mode of the device to AC.
        """

        if self.epc.query('M?') == "Work Mode: AC(Triangle)":
            pass
        else:
            self.epc.write('MAC')

        return

    def setDC(self):
        """
        This function will change the mode of the device to DC.
        """

        if self.epc.query('M?') == "Work Mode: DC":
            pass
        else:
            self.epc.write('MDC')

        return

    def getf(self):
        """
        This function will output the present scambling frequency.
        """
        self.epc.flush(64)

        f = self.epc.query('F?')

        return f

    def intf(self):
        """
        This will initialize the frequency for the 4 channels to 0 Hz.
        """

        self.epc.write('F1,0')
        self.epc.write('F2,0')
        self.epc.write('F3,0')
        self.epc.write('F4,0')

        return

    def changef(self, channel, frequency):
        """

        This function will set the selected channel to frequency f.

        Args:
            channel (int): channel number (1~4)
            frequency (int): frequency that you want to change (0~100)
        """

        self.epc.write("F{},{}".format(channel, frequency))

        return

    def getV(self):
        """
        This function will output the voltage reading of all the 4 channels.
        """

        self.epc.flush(64)
        V = self.epc.query('V?')

        time.sleep(0.1)
        return V

    def setV(self, channel, voltage):
        """
        This function will set the voltage for channel n.

        Args:
            channel (int)): channel number (1~4)
            voltage (int): voltage that you want to change (-5000mv ~ +5000mv)
        """

        self.epc.write("V{},{}".format(channel, voltage))

        string = "V{},{}".format(channel, voltage)
        time.sleep(0.1)
        return

    def setVString(self, channel, voltage):
        """
        This function will set the voltage for channel n.

        Args:
            channel (int)): channel number (1~4)
            voltage (int): voltage that you want to change (-5000mv ~ +5000mv)
        """
        localstr = "V{},{}".format(channel, voltage)
        self.epc.write(localstr)

        time.sleep(0.1)
        return localstr

    def setVzero(self, channel):
        """
        This function will set the voltage of the corresponding channel to zero.


        Args:
            channel (int): channel number (1~4)
        """

        self.epc.write('VZ{}'.format(channel))

        return

    def DC_output_AC_mode(self, i):
        """
        This function allow user to output a fixed DC voltage while unit is operating in the AC mode. 


        Args:
            i (int): 0 or 1. (0 for disable, 1 for enable)
        """

        self.epc.write('ENVF{}'.format(i))

        return

    def getopmode(self):
        """
        This function will output the present operating mode for the four channels.
        THis function will only output the mode for each of the four channels when DC output with AC mode is enabled.
        """
        self.epc.flush(64)
        mode = self.epc.query('VF?')

        return mode

    def VFchange(self, channel):
        """
        This function will toggle the opearting mode for the corresponding channel from voltage mode to frequency mode.

        Args:
            channel (int): channel number (1~4)
        """

        self.epc.write('VF{}'.format(channel))

        return

    def getwaveform(self):
        """
        This function will return the present waveform type
        """
        self.epc.flush(64)
        waveform = self.epc.query('WF?')

        return waveform

    def changesinewave(self):
        """
        This function will change the output waveform to sine wave.
        """
        self.epc.write('WF1')

        return

    def changetriwave(self):
        """
        This function will change the output waveform to triangle wave.
        """

        self.epc.write('WF2')

        return

    def randomiseV(self):
        """
        Set all channel voltages to random value.

        `voltages` is a list of size 4 containing the voltage values.
        """
        randomlist = []
        for i in range(0, 3):

            n = random.randint(-2000, 2000)
            randomlist.append(n)
        # print(randomlist)

        for j in range(1, 4):
            self.setV(j, randomlist[j-1])
        return

    def setAllVoltages(self, voltages):
        """
        Set all channel voltages.

        `voltages` is a list of size 4 containing the voltage values.
        """
        for i in range(1, 5):
            self.setV(i, voltages[i-1])
        return

    def intV(self):
        """
        This function will initialize the voltage for all the 4 channels.
        """

        self.setAllVoltages([0, 0, 0, 0])

        return

    def setMinVoltage(self):
        """
        Set the all the channels to -5000mv.

        Returns
        -------
        None.

        """
        for i in range(1, 4):
            self.setV(i, -5000)

        return

    def getVArray(self):
        self.epc.flush(64)
        V = self.getV()
        B = V.split()
        vArray = []

        V1 = B[2]
        vArray.append(int(float(V1)))
        V2 = B[4]
        vArray.append(int(float(V2)))
        V3 = B[6]
        vArray.append(int(float(V3)))
        V4 = B[8]
        vArray.append(int(float(V4)))

        return vArray
