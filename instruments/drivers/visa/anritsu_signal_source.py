# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyHqcLegacy Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Drivers for Anritsu instrument using VISA library.

"""
import re
from textwrap import fill
from inspect import cleandoc

from visa import VisaTypeError

from ..driver_tools import (InstrIOError, secure_communication,
                            instrument_property)
from ..visa_tools import VisaInstrument


class AnritsuMG3694(VisaInstrument):
    """Driver for the Anritsu MG 3694 microwave source.

    """

    def __init__(self, connection_info, caching_allowed=True,
                 caching_permissions={}, auto_open=True):
        super(AnritsuMG3694, self).__init__(connection_info,
                                            caching_allowed,
                                            caching_permissions,
                                            auto_open)
        self.frequency_unit = 'GHz'

    def open_connection(self, **para):
        """Open the connection to the instr using the `connection_str`.

        """
        super(AnritsuMG3694, self).open_connection(**para)
        self.write_termination = '\n'
        self.read_termination = '\n'
        self.write("DSPL 4")
        self.write("EBW3")  # if the external reference is very stable in phase
                            # the largest EBW must be chosen
        self.write("LO0")   # no offset on the power
        self.write("LOG")   # Selects logarithmic power level operation in dBm
        self.write("TR1")   # Sets 40 dB of attenuation when RF is switched off
        self.write("PS1")   # Turns on the Phase Offset
        self.write("DS1")   # Turns off the secure mode
        self.write("AT1")   # Selects ALC step attenuator decoupling
        self.write("IL1")   # Selects internal leveling of output power

    @instrument_property
    @secure_communication()
    def frequency(self):
        """Frequency getter method
        """
        freq = self.query('FREQ?')
        if freq:
            freq = float(freq)
            if self.frequency_unit == 'GHz':
                return freq/1e9
            elif self.frequency_unit == 'MHz':
                return freq/1e6
            elif self.frequency_unit == 'kHz':
                return freq/1e3
            else:
                return freq
        else:
            raise InstrIOError('Anritsu did not return its frequency')

    @frequency.setter
    @secure_communication()
    def frequency(self, value):
        """Frequency setter method
        """
        unit = self.frequency_unit
        self.write('FREQ {}{}'.format(value, unit))
        result = self.query('FREQ?')
        if result:
            result = float(result)
            if unit == 'GHz':
                result /= 1e9
            elif unit == 'MHz':
                result /= 1e6
            elif unit == 'kHz':
                result /= 1e3
            if abs(result - value) > 10**-12:
                mes = 'Instrument did not set correctly the frequency'
                raise InstrIOError(mes)
        else:
            raise InstrIOError('Anritsu did not return its frequency')

    @instrument_property
    @secure_communication()
    def power(self):
        """Power getter method
        """
        power = self.query(':POW?')
        if power:
            return float(power)
        else:
            raise InstrIOError('Anritsu did not return its power')

    @power.setter
    @secure_communication()
    def power(self, value):
        """Power setter method
        """
        self.write('POW {}'.format(value))
        result = self.query('POW?')
        if result:
            if abs(float(result) - value) > 10**-12:
                raise InstrIOError('Instrument did not set correctly the power')
        else:
            raise InstrIOError('Anritsu did not return its power')

    @instrument_property
    @secure_communication()
    def output(self):
        """Output getter method
        """
        output = self.query('OUTP?')
        if output == '1':
            return 'ON'
        elif output == '0':
            return 'OFF'
        else:
            mes = 'Anritsu signal source did not return its output'
            raise InstrIOError(mes)

    @output.setter
    @secure_communication()
    def output(self, value):
        """Output setter method. 'ON', 'OFF'
        """

        on = re.compile('on', re.IGNORECASE)
        off = re.compile('off', re.IGNORECASE)
        if on.match(value) or value == 1:

            self.write('OUTP 1')
            if self.query('OUTP?') != '1':
                raise InstrIOError(cleandoc('''Instrument did not set correctly
                                        the output'''))
        elif off.match(value) or value == 0:
            self.write('OUTP 0')
            if self.query('OUTP?')[0] != '0':
                raise InstrIOError(cleandoc('''Instrument did not set correctly
                                        the output'''))
        else:
            mess = fill(cleandoc('''The invalid value {} was sent to
                        switch_on_off method''').format(value), 80)
            raise VisaTypeError(mess)
