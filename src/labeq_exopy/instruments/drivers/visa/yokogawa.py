# Jake Macdonald 7/8/2022

import re
from textwrap import fill
from inspect import cleandoc

from ..driver_tools import (InstrIOError, instrument_property,
                            secure_communication)
from ..visa_tools import VisaInstrument, errors


import time
import pyvisa
from time import sleep
from multiprocessing import Process
from multiprocessing import current_process


######################################################################################################### Jake Additions

# def ramp (name, duration, initVal, goal) : 
#     rm = pyvisa.ResourceManager()
#     inst = rm.open_resource(name)
    
#     start = time.time()
#     dif = goal - initVal
#     percent = 0

#     while percent < 1 :
#         percent = (time.time() - start) /duration
#         if (percent >= 0.99) :
#             inst.write ('Sour:lev ' + str(goal))
#             break

#         inst.write ('Sour:lev ' + str(initVal + (dif * percent)))
#         sleep(.05)

def measure(thing):
    value = thing.query(":SOURce:LEV?")
    if value:
        return float(value)
    else:
        raise InstrIOError('Instrument did not return the value')

def resistance(thing) :
    thing.write('SOUR:FUNC VOLT')
    volt = measure(thing)
    thing.write('SOUR:FUNC CURR')
    current = measure(thing)

    if not current :
        return "aproaching infinite"
    
    value = (volt / current)
    if value:
        return float(value)
    else:
        raise InstrIOError('Resistance measure failed')
    
def setSource(thing, point) :
    thing.write('SOUR:LEV ' + str(point))
    return "success"
   


class YokogawaGS200(VisaInstrument):
    
    @secure_communication()
    def source_voltage_dc(self, value) :
        self.write('sour:func volt')
        return setSource(self,value)


    @secure_communication()
    def source_current_dc(self, value) :
        self.write('sour:func curr')
        return setSource(self,value)


    @secure_communication()
    def read_voltage_dc(self):
        self.write('SOUR:FUNC VOLT')
        return measure(self)

    @secure_communication()
    def read_current_dc(self):
        self.write('SOUR:FUNC CURR')
        return measure(self)


    @secure_communication()
    def read_two_resistance(self):
        return resistance(self)

    @secure_communication()
    def read_four_resistance(self):
        self.write('sens:rem 1')
        value = resistance(self)
        self.write('sens:rem 0')
        return value
    
    @secure_communication()
    def set_range_yoko(self, range_val, funcVal):
        self.write('SOUR:FUNC '+funcVal)

        if range_val == 'MAX' or not range_val :
            self.write("sour:rang max")
            return "success"

        self.write('sour:RANG '+ str(range_val))
        return "success"
    

 

    @secure_communication()
    def set_ramp(self, rampVal, funcVal, useBetter, goalVal):
        self.write('SOUR:FUNC '+funcVal)
        
        if goalVal > float(self.query('sour:rang?')): 
            raise Exception("Target value exceeds range")

        if (useBetter == 'True') :
            if __name__ == 'labeq_exopy.instruments.drivers.visa.yokogawa':
                print (self.connection_str)
                thisProcess = current_process()
                thisProcess.daemon = False
                initVal = float(self.query('sour:lev?'))
                start = time.time()
                dif = float(goalVal) - initVal
                percent = 0

                while percent < 1 :
                    percent = (time.time() - start) /float(rampVal)
                    if (percent >= 0.99) :
                        self.write ('Sour:lev ' + str(goalVal))
                        break

                    self.write ('Sour:lev ' + str(initVal + (dif * percent)))
                    sleep(.05)
                
        else:
            self.write('prog:slop '+rampVal)
            self.write('sour:lev '+ goalVal)

        return "success"
    
#############################################################################################################
    def open_connection(self, **para):
        """Open the connection to the instr using the `connection_str`.

        """
        super(YokogawaGS200, self).open_connection(**para)
        self.write_termination = '\n'
        self.read_termination = '\n'
        self.write('*CLS')
   

    def check_connection(self):
        """
        """
        return False


class Yokogawa7651(VisaInstrument):
    """
    Driver for the Yokogawa7651, using the VISA library.

    This driver does not give access to all the functionnality of the
    instrument but you can extend it if needed. See the documentation of the
    `driver_tools` package for more details about writing instruments drivers.

    Parameters
    ----------
    see the `VisaInstrument` parameters in the `driver_tools` module

    Attributes
    ----------
    voltage : float, instrument_property
        Voltage at the output of the generator in volts.
    function : str, instrument_property
        Current function of the generator can be either 'VOLT' or 'CURR' (case
        insensitive).
    output : bool, instrument_property
        State of the output 'ON'(True)/'OFF'(False).

    """
    def open_connection(self, **para):
        """Open the connection to the instr using the `connection_str`.

        """
        super(Yokogawa7651, self).open_connection(**para)
        self.write_termination = '\n'
        self.read_termination = '\n'

    @instrument_property
    @secure_communication()
    def voltage(self):
        """Voltage getter method.

        """
        data = self.query("OD")
        voltage = float(data[4::])
        if voltage is not None:
            return voltage
        else:
            raise InstrIOError('Instrument did not return the voltage')

    @voltage.setter
    @secure_communication()
    def voltage(self, set_point):
        """Voltage setter method.

        """
        self.write("S{:+E}E".format(set_point))
        data = self.query("OD")
        value = float(data[4::])
        # to avoid floating point rouding
        if abs(value - round(set_point, 9)) > 10**-9:
            raise InstrIOError('Instrument did not set correctly the voltage')

    @instrument_property
    @secure_communication()
    def function(self):
        """Function getter method.

        """
        data = self.query('OD')
        if data[3] == 'V':
            return 'VOLT'
        elif data[3] == 'A':
            return 'CURR'
        else:
            raise InstrIOError('Instrument did not return the function')

    @function.setter
    @secure_communication()
    def function(self, mode):
        """Function setter method.

        """
        volt = re.compile('VOLT', re.IGNORECASE)
        curr = re.compile('CURR', re.IGNORECASE)
        if volt.match(mode):
            self.write('OS')
            self.read()
            current_range = self.read()[2:4]
            # Empty output buffer.
            self.read()
            self.read()
            self.read()
            self.write('F1{}E'.format(current_range))
            value = self.query('OD')
            if value[3] != 'V':
                raise InstrIOError('Instrument did not set correctly the mode')
        elif curr.match(mode):
            self.write('F5E')
            value = self.query('OD')
            if value[3] != 'A':
                raise InstrIOError('Instrument did not set correctly the mode')
        else:
            mess = fill('''The invalid value {} was sent to set_function
                        method of the Yokogawa driver'''.format(value), 80)
            raise errors.VisaTypeError(mess)

    @instrument_property
    @secure_communication()
    def output(self):
        """Output getter method.

        """
        mess = self.query('OC')[5::]
        value = ('{0:08b}'.format(int(mess)))[3]
        if value == '0':
            return 'OFF'
        elif value == '1':
            return 'ON'
        else:
            raise InstrIOError('Instrument did not return the output state')

    @output.setter
    @secure_communication()
    def output(self, value):
        """Output setter method.

        """
        on = re.compile('on', re.IGNORECASE)
        off = re.compile('off', re.IGNORECASE)
        if on.match(value) or value == 1:
            self.write('O1E')
            mess = self.query('OC')[5::]  # Instr return STS1=m we want m
            if ('{0:08b}'.format(int(mess)))[3] != '1':
                raise InstrIOError(cleandoc('''Instrument did not set correctly
                                            the output'''))
        elif off.match(value) or value == 0:
            self.write('O0E')
            mess = self.query('OC')[5::]  # Instr return STS1=m we want m
            if('{0:08b}'.format(int(mess)))[3] != '0':
                raise InstrIOError(cleandoc('''Instrument did not set correctly
                                            the output'''))
        else:
            mess = fill(cleandoc('''The invalid value {} was sent to set the
                    output state of the Yokogawa driver''').format(value), 80)
            raise errors.VisaTypeError(mess)

    def check_connection(self):
        """
        """
        return False
