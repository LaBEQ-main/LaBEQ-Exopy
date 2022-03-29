# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyHqcLegacy Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Base classes for instrument relying on the VISA protocol.

"""
import re
from textwrap import fill
from inspect import cleandoc

from ..driver_tools import (InstrIOError, instrument_property,
                            secure_communication)
from ..visa_tools import VisaInstrument, errors


class YokogawaGS200(VisaInstrument):
    """
    Driver for the YokogawaGS200, using the VISA library.

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
        super(YokogawaGS200, self).open_connection(**para)
        self.write_termination = '\n'
        self.read_termination = '\n'
        self.write('*CLS')

    @instrument_property
    @secure_communication()
    def voltage(self):
        """Voltage getter method. NB: does not check the current function.

        """
        voltage = self.query(":SOURce:LEVel?")
        if voltage:
            return float(voltage)
        else:
            raise InstrIOError('Instrument did not return the voltage')

    @secure_communication()
    def read_voltage_dc(self):
        """Wrapper for the voltage getter that checks for the mode

        """
        if self.function == 'VOLT':
            return self.voltage
        msg = ('Instrument cannot read its voltage when in current mode')
        raise InstrIOError(msg)

    @voltage.setter
    @secure_communication()
    def voltage(self, set_point):
        """Voltage setter method. NB: does not check the current function.

        """
        self.write(":SOURce:LEVel {}".format(set_point))
        value = self.query('SOURce:LEVel?')
        # to avoid floating point rouding
        if abs(float(value) - round(set_point, 9)) > 10**-9:
            raise InstrIOError('Instrument did not set correctly the voltage')

    @instrument_property
    @secure_communication()
    def voltage_range(self):
        """ Voltage range getter method.

        NB: does not check the current function.

        """
        v_range = self.query(":SOURce:RANGe?")
        if v_range is not None:
            if v_range == '10E-3':
                return '10 mV'
            elif v_range == '100E-3':
                return '100 mV'
            elif v_range == '1E+0':
                return '1 V'
            elif v_range == '10E+0':
                return '10 V'
            elif v_range == '30E+0':
                return '30 V'
        else:
            raise InstrIOError('Instrument did not return the range')

    @voltage_range.setter
    @secure_communication()
    def voltage_range(self, v_range):
        """Voltage range getter method.

        NB: does not check the current function.

        """
        visa_range = ''
        if v_range == '10 mV':
            visa_range = '10E-3'
        elif v_range == '100 mV':
            visa_range = '100E-3'
        elif v_range == '1 V':
            visa_range = '1E+0'
        elif v_range == '10 V':
            visa_range = '10E+0'
        elif v_range == '30 V':
            visa_range = '30E+0'

        if visa_range:
            self.write(":SOURce:RANGe {}".format(visa_range))
            check = self.query(":SOURce:RANGe?")
            if check != visa_range:
                raise InstrIOError(cleandoc('''Instrument did not set correctly
                    the range'''))

    @instrument_property
    @secure_communication()
    def current(self):
        """Current getter method.

        NB: does not check the current function.

        """
        current = self.query(":SOURce:LEVel?")
        if current:
            return float(current)
        else:
            raise InstrIOError('Instrument did not return the current')

    @current.setter
    @secure_communication()
    def current(self, set_point):
        """Current setter method.

        NB: does not check the current function.

        """
        self.write(":SOURce:LEVel {}".format(set_point))
        value = self.query('SOURce:LEVel?')
        # to avoid floating point rouding
        if abs(float(value) - round(set_point, 9)) > 10**-9:
            raise InstrIOError('Instrument did not set correctly the current')

    @instrument_property
    @secure_communication()
    def current_range(self):
        """ Current range getter method.

        NB: does not check the current function.

        """
        c_range = self.query(":SOURce:RANGe?")
        if c_range is not None:
            if c_range == '1E-3':
                return '1 mA'
            elif c_range == '10E-3':
                return '10 mA'
            elif c_range == '100E-3':
                return '100 mA'
            elif c_range == '200E-3':
                return '200 mA'
        else:
            raise InstrIOError('Instrument did not return the range')

    @voltage_range.setter
    @secure_communication()
    def current_range(self, c_range):
        """Voltage range getter method.

        NB: does not check the current function.

        """
        visa_range = ''
        if c_range == '1 mA':
            visa_range = '1E-3'
        elif c_range == '10 mA':
            visa_range = '10E-3'
        elif c_range == '100 mA':
            visa_range = '100E-3'
        elif c_range == '200 mA':
            visa_range = '200E-3'

        if visa_range:
            self.write(":SOURce:RANGe {}".format(visa_range))
            check = self.query(":SOURce:RANGe?")
            if check != visa_range:
                raise InstrIOError(cleandoc('''Instrument did not set correctly
                    the range'''))

    @instrument_property
    @secure_communication()
    def function(self):
        """Function getter method

        """
        value = self.query('SOURce:FUNCtion?')
        if value:
            return value
        else:
            raise InstrIOError('Instrument did not return the function')

    @function.setter
    @secure_communication()
    def function(self, mode):
        """Function setter method

        """
        volt = re.compile('VOLT', re.IGNORECASE)
        curr = re.compile('CURR', re.IGNORECASE)
        if self.voltage == 0 and self.output is False:
            if volt.match(mode):
                self.write(':SOURce:FUNCtion VOLT')
                value = self.query('SOURce:FUNCtion?')
                if value != 'VOLT':
                    raise InstrIOError('Instrument did not set correctly the'
                                       'mode')
            elif curr.match(mode):
                self.write(':SOURce:FUNCtion CURR')
                value = self.query('SOURce:FUNCtion?')
                if value != 'CURR':
                    raise InstrIOError('Instrument did not set correctly the'
                                       'mode')
            else:
                mess = fill('''The invalid value {} was sent to set_function
                            method of the Yokogawa driver'''.format(value), 80)
                raise errors.VisaTypeError(mess)
        else:
            mess = ''' Set current/voltage to 0 and output off to change the
                    function mode of a Yokogawa. Currently voltage/current = {}
                    and output is {}'''
            raise InstrIOError(mess.format(self.voltage, self.output))

    @instrument_property
    @secure_communication()
    def output(self):
        """Output getter method

        """
        value = self.query(':OUTPUT?')
        if value:
            return bool(int(value))
        else:
            raise InstrIOError('Instrument did not return the output state')

    @output.setter
    @secure_communication()
    def output(self, value):
        """Output setter method

        """
        on = re.compile('on', re.IGNORECASE)
        off = re.compile('off', re.IGNORECASE)
        # output is only switched on if voltage or current is 0
        # note that self.voltage gets the source level, which is the voltage
        # in voltage mode, and the current in current mode.
        if self.voltage == 0:
            if on.match(value) or value == 1:
                self.write(':OUTPUT ON')
                if self.query(':OUTPUT?') != '1':
                    raise InstrIOError(cleandoc('''Instrument did not set
                                                correctly the output'''))
            elif off.match(value) or value == 0:
                self.write(':OUTPUT OFF')
                if self.query(':OUTPUT?') != '0':
                    raise InstrIOError(cleandoc('''Instrument did not set
                                                correctly the output'''))
            else:
                mess = fill(cleandoc('''The invalid value {} was sent to set
                                     the output state of the Yokogawa
                                     driver''').format(value), 80)
                raise errors.VisaTypeError(mess)
        else:
            msg = 'set volage/current to 0 to change the DC output'
            raise InstrIOError(msg)

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

    @secure_communication()
    def read_voltage_dc(self):
        """Wrapper for the voltage getter that checks for the mode

        """
        if self.function == 'VOLT':
            return self.voltage
        msg = ('Instrument cannot read its voltage when in current mode')
        raise InstrIOError(msg)


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
