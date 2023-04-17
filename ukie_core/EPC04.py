import pyvisa as visa
import time
import random

import numpy as np


### Import the necessary Libraries###
'''
This code is just using 3 channels.
'''


class EPCdriver:
    
    voltage_lim = (-5. , 5.)
    frequency_lim = (0 , 100)
    

    """
    This will control the function of the electric polarization controller
    """
    
    def __init__(self , EPCAddress ='ASRL3::INSTR'):
        """
        This will initialize visa and connect to the device (EPC).

        Args:
            EPC_address (str): Address of the device. ''.
        """
        
        rm = visa.ResourceManager()

        
        self.EPC = rm.open_resource(EPCAddress)
        #self.EPC.variable('voltage', self.getV, self.intV, self.changeV)
        #self.EPC.variable('mode', self.getmode, self.setAC, self.setDC, self.DC_output_AC_mode, self.getopmode, self.VFchange,self.setVmax,self.setVmin, self.setVzero)
        #self.EPC.variable('frequency', self.getf, self.intf, self.changef)
        #self.EPC.variable('waveform', self.getwaveform, self.changesinewave, self.changetriwave)

        self.EPC.write_termination = '\r\n'
        self.EPC.read_termination = '\r\n'
        #.EPC.timeout(1000)
       
        return
    
    def _parse_response(self, comm, resp):
        resp=[s.strip() for s in resp.splitlines() if s.strip()]
        if resp and (resp[0]==comm):
            resp=resp[1:]
           
        resp=resp[:-1]
        return resp
    
    '''def query(self, comm, prefix=None, prefix_line=None, timeout=None):
        """
        Query the device.

        If `prefix` is not ``None``, it can specify a string which should be at the beginning of the `prefix_line` line of the reply.
        If it is present, it is removed and the rest of that line is returned; otherwise, an error is raised.
        If `prefix_line` is ``None``, return the first reply line beginning with the given prefix value (or raise an error if not such line is present).
        """
        comm=comm.strip()
        self.EPC.flush_read()
        self.EPC.write(comm)
        resp=self.EPC.read_multichar_term(["Done\r\n","Error!\r\n"],timeout=timeout)
        resp=self._parse_response(comm,resp)
        if prefix:
            if prefix_line is None:
                for ln in resp:
                    ln=ln.upper()
                    if ln.startswith(prefix.upper()):
                        return ln[len(prefix):].strip()
            else:
                ln=resp[prefix_line].upper()
                if ln.startswith(prefix.upper()):
                    return ln[len(prefix):].strip()
            raise OZOpticsError("unexpected reply: {}".format(resp))
        return resp'''
    
    '''def flush_read(self):
      """Flush the device output (read all the available data; return the number of bytes read)"""
      return len(self.read()) ''' 
  

    
    '''def query(self, comm):
        comm=comm.strip()
        #self.EPC.read()
        self.EPC.write(comm)
        #resp=self.EPC.read_multichar_term(["Done\r\n","Error!\r\n"],remove_term=False)
        return self._parse_response(comm,resp)'''
    
    def flush_read(self):
        """Flush the device output (read all the available data; return the number of bytes read)"""
        return len(self.read())
    

    
    def getmode(self):
        """
        This function will tell us the mode (AC/DC) of the device that is opearting.
        """
        self.EPC.flush(64)
        mode = self.EPC.query('M?')
        

        
        
        
        return mode
    
    def setAC(self):
        """
        This function will change the mode of the device to AC.
        """
        
        
        if self.EPC.query('M?') == "Work Mode: AC(Triangle)":
            pass
        else:
            self.EPC.write('MAC')
            
            
        return
    
    def setDC(self):
        """
        This function will change the mode of the device to DC.
        """
        
        if self.EPC.query('M?') == "Work Mode: DC":
            pass
        else:
            self.EPC.write('MDC')
            
        return
    
    def getf(self):
        """
        This function will output the present scambling frequency.
        """
        self.EPC.flush(64)

        f = self.EPC.query('F?')
        
        

        
        return f
    
    
    
    def intf(self):
        """
        This will initialize the frequency for the 4 channels to 0 Hz.
        """
        
        self.EPC.write('F1,0')
        self.EPC.write('F2,0')
        self.EPC.write('F3,0')
        self.EPC.write('F4,0')
        

        return
    
    def changef(self , channel , frequency):
        """
        
        This function will set the selected channel to frequency f.

        Args:
            channel (int): channel number (1~4)
            frequency (int): frequency that you want to change (0~100)
        """
        
        self.EPC.write("F{},{}".format(channel , frequency))
        
        return
        

        
    def getV(self):
        """
        This function will output the voltage reading of all the 4 channels.
        """
        
        self.EPC.flush(64)
        V = self.EPC.query('V?')
        
        time.sleep(0.1)
        return V

    
    
    def setV(self , channel , voltage):
        """
        This function will set the voltage for channel n.

        Args:
            channel (int)): channel number (1~4)
            voltage (int): voltage that you want to change (-5000mv ~ +5000mv)
        """
        
        self.EPC.write("V{},{}".format(channel , voltage))
        
        string = "V{},{}".format(channel , voltage)
        time.sleep(0.1)
        return 
        
    
    def setVString(self , channel , voltage):
        """
        This function will set the voltage for channel n.

        Args:
            channel (int)): channel number (1~4)
            voltage (int): voltage that you want to change (-5000mv ~ +5000mv)
        """
        localstr = "V{},{}".format(channel , voltage)
        self.EPC.write(localstr)
        
        time.sleep(0.1)
        return localstr

    
    def setVzero(self , channel):
        """
        This function will set the voltage of the corresponding channel to zero.


        Args:
            channel (int): channel number (1~4)
        """
        
        self.EPC.write('VZ{}'.format(channel))
        

        return

    
    def DC_output_AC_mode(self,i):
        """
        This function allow user to output a fixed DC voltage while unit is operating in the AC mode. 
    

        Args:
            i (int): 0 or 1. (0 for disable, 1 for enable)
        """
        
        self.EPC.write('ENVF{}'.format(i))

        return
    
    def getopmode(self):
        
        """
        This function will output the present operating mode for the four channels.
        THis function will only output the mode for each of the four channels when DC output with AC mode is enabled.
        """
        self.EPC.flush(64)
        mode = self.EPC.query('VF?')
        

        return mode
    
    def VFchange(self, channel):
        """
        This function will toggle the opearting mode for the corresponding channel from voltage mode to frequency mode.

        Args:
            channel (int): channel number (1~4)
        """
        
        self.EPC.write('VF{}'.format(channel))
        

        return
    
    def getwaveform(self):
        
        """
        This function will return the present waveform type
        """
        self.EPC.flush(64)
        waveform = self.EPC.query('WF?')
        

        
        return waveform
    
    def changesinewave(self):
        
        """
        This function will change the output waveform to sine wave.
        """
        self.EPC.write('WF1')
        
        
        return
    
    def changetriwave(self):
        
        """
        This function will change the output waveform to triangle wave.
        """
        
        self.EPC.write('WF2')

        return
    
    def randomiseV(self):
        """
        Set all channel voltages to random value.

        `voltages` is a list of size 4 containing the voltage values.
        """
        randomlist = []
        for i in range(0,3):
            
            n = random.randint(-2000,2000)
            randomlist.append(n)
        #print(randomlist)

        for j in range(1,4): 
            self.setV(j, randomlist[j-1]) 
        return
    
    def setAllVoltages(self, voltages):
        """
        Set all channel voltages.

        `voltages` is a list of size 4 containing the voltage values.
        """
        for i in range(1, 5): 
            self.setV(i , voltages[i-1])
        return
    
    def intV(self):
        """
        This function will initialize the voltage for all the 4 channels.
        """
        
        self.setAllVoltages([0,0,0,0])
        

        return
    
    
    def setMinVoltage(self):
        """
        Set the all the channels to -5000mv.

        Returns
        -------
        None.

        """
        for i in range(1,4):
            self.setV(i , -5000)
            
        return
    
    def getVArray(self):
        self.EPC.flush(64)
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
    
    '''def getVArray(self):
        """
        This function will output the voltage reading of all the 4 channels in list.
        """
        
        self.EPC.flush(64)
        V = self.EPC.query('V?')
        
        
        
        
        b = V.split()


        Vlist=[]
        for i in b:
            if i.startswith('+') == True or i.startswith('-') == True:
                Vlist += i


                

        reducedVlist = [Vlist[i:i+5] for i in range(0, len(Vlist), 5)]


        voltages = []
        #finalVoltages = []
        #global finalVoltages


        for i in reducedVlist:
            Velement = 0
            V = 0
            
            if i[0] == '-':
                for n in range(1,len(i)):

                    VDigit = int(i[n])
                    Velement = ((-1)*VDigit*(10**(len(i)-n-1)))
                    V = V + Velement
            
            elif i[0] == '+':
                for n in range(1,len(i)):

                    VDigit = int(i[n])
                    Velement = (VDigit*(10**(len(i)-n-1)))
                    V = V + Velement
                    
                    
            else:
                self.EPC.getV()
                print('1')
                 
            
            
            voltages.append(V)
            
            finalVoltages = voltages[:-1]
            
        
            
            


        
        return finalVoltages'''

    '''def getVArray(self):
        """
        This function will output the voltage reading of all the 4 channels in list.
        """
        
        V = self.getV()
        print('hello, ' + V)
        
        if len(V.split()) < 6:
            return self.getVArray()
        
        else:
            b = V.split()
            Vlist=[]
            for i in b:
                if i.startswith('+') == True or i.startswith('-') == True:
                    Vlist += i
                
            reducedVlist = [Vlist[i:i+5] for i in range(0, len(Vlist), 5)]


            voltages = []
            #finalVoltages = []
            #global finalVoltages


            for i in reducedVlist:
                Velement = 0
                V = 0
                
                if i[0] == '-':
                    for n in range(1,len(i)):

                        VDigit = int(float(i[n]))
                        Velement = ((-1)*VDigit*(10**(len(i)-n-1)))
                        V = V + Velement
                
                elif i[0] == '+':
                    for n in range(1,len(i)):

                        VDigit = int(float(i[n]))
                        Velement = (VDigit*(10**(len(i)-n-1)))
                        V = V + Velement
                        
                        
                else:
                    self.EPC.getV()
                    print('1')
                     
                
                voltages.append(V)
                
                finalVoltages = voltages[:-1]
                

            
            return finalVoltages'''


        

'''
a = EPC.getV()

b = a.split()


Vlist=[]
for i in b:
    if i.startswith('+') == True or i.startswith('-') == True:
        Vlist += i


        

reducedVlist = [Vlist[i:i+5] for i in range(0, len(Vlist), 5)]


voltages = []


for i in reducedVlist:
    Velement = 0
    V = 0
    
    if i[0] == '-':
        for n in range(1,len(i)):

            VDigit = int(i[n])
            Velement = (-1)*VDigit*(10**(len(i)-n-1))
            V = V + Velement
    
    if i[0] == '+':
        for n in range(1,len(i)):

            VDigit = int(i[n])
            Velement = VDigit*(10**(len(i)-n-1))
            V = V + Velement
         
    
    
    voltages.append(V)
    
print(voltages)
'''
'''
voltage = []
def parseResponseVoltage(VoltageReading):
    b = VoltageReading.split()


    Vlist=[]
    for i in b:
        if i.startswith('+') == True or i.startswith('-') == True:
            Vlist += i


    #for i in Vlist:
        #if i =='+' or i=='-':
            #Vlist.remove(i)
            

    reducedVlist = [Vlist[i:i+5] for i in range(0, len(Vlist), 5)]


    


    for i in reducedVlist:
        Velement = 0
        V = 0
        
        if i[0] == '-':
            for n in range(1,len(i)):

                VDigit = int(i[n])
                Velement = (-1)*VDigit*(10**(len(i)-n-1))
                V = V + Velement
        
        if i[0] == '+':
            for n in range(1,len(i)):

                VDigit = int(i[n])
                Velement = VDigit*(10**(len(i)-n-1))
                V = V + Velement
             
        
        
        voltage.append(V)
        
    print(voltage)
    return
'''

#%%

