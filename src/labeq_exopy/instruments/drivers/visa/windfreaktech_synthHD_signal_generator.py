# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyHqcLegacy Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Driver for Windfreaktech SynthHD SignalGenerator using VISA library.

"""
import re
from textwrap import fill
from inspect import cleandoc

from visa import VisaTypeError

from ..driver_tools import (InstrIOError, instrument_property,
                            secure_communication)
from ..visa_tools import VisaInstrument

CONVERSION_FACTORS = {'GHz': {'Hz': 1e9, 'kHz': 1e6, 'MHz': 1e3, 'GHz': 1},
                      'MHz': {'Hz': 1e6, 'kHz': 1e3, 'MHz': 1, 'GHz': 1e-3},
                      'kHz': {'Hz': 1e3, 'kHz': 1, 'MHz': 1e-3, 'GHz': 1e-6},
                      'Hz': {'Hz': 1, 'kHz': 1e-3, 'MHz': 1e-6, 'GHz': 1e-9}}


class SynthHD(VisaInstrument):
    """Driver for WindFreakTech's synthHD SignalGenerator.

    This driver does not give access to all the functionnality of the
    instrument but you can extend it if needed. See the documentation of
    the driver_tools module for more details about writing instruments
    drivers.

    Parameters
    ----------
    see the `VisaInstrument` parameters

    Attributes
    ----------
    frequency_unit : str
        Frequency unit used by the driver. The default unit is 'GHz'. Other
        valid units are : 'MHz', 'KHz', 'Hz'
    frequency : float, instrument_property
        Fixed frequency of the output signal.
    power : float, instrument_property
        Fixed power of the output signal.
    output : bool, instrument_property
        State of the output 'ON'(True)/'OFF'(False).

    """

    def __init__(self, connection_info, caching_allowed=True,
                 caching_permissions={}, auto_open=True):

        super(SynthHD, self).__init__(connection_info, caching_allowed,
                                      caching_permissions, auto_open)
        self.frequency_unit = 'GHz'
        self.write_termination = ''
        self.read_termination = ''

    @instrument_property
    @secure_communication()
    def channel(self):
        """Selected channel.

        """
        output = self.query('C?')
        if output:
            channel = int(output)
            return channel
        else:
            mes = 'Instrument did not return its channel'
            raise InstrIOError(mes)

    @channel.setter
    @secure_communication()
    def channel(self, value):
        """Channel setter method.

        """
        self.write('C{}'.format(value))
        output = self.query('C?')
        if output:
            if int(output) != int(value):
                mes = 'Instrument did not set the channel correctly'
                raise InstrIOError(mes)
        else:
            mes = 'Instrument did not return its channel'
            raise InstrIOError(mes)

    @instrument_property
    @secure_communication()
    def frequency(self):
        """Frequency of the output signal.

        """
        freq = self.query('f?')
        if freq:
            return float(freq)
        else:
            mes = 'Instrument did not return the frequency'
            raise InstrIOError(mes)

    @frequency.setter
    @secure_communication()
    def frequency(self, value):
        """Frequency setter method.

        """
        unit = self.frequency_unit
        valueMHz = value*CONVERSION_FACTORS[unit]['MHz']
        valueMHz_format = '{:.4f}'.format(valueMHz)
        self.write('f{}'.format(valueMHz_format))
        result = float(self.query('f?'))  # asks for frequency of current channel in MHz
        if abs(result - valueMHz) > 1e-12:
            mes = 'Instrument did not set correctly the frequency'
            raise InstrIOError(mes)
        self.check_calibration()

    @instrument_property
    @secure_communication()
    def power(self):
        """Power of the output signal.

        """
        power = self.query('W?')
        if power:
            return float(power)
        else:
            mes = 'Instrument did not return the power'
            raise InstrIOError(mes)

    @power.setter
    @secure_communication()
    def power(self, value):
        """Power setter method.

        """
        self.write('W{:.4f}'.format(value))
        result = float(self.query('W?'))
        if abs(result - value) > 10**-12:
            raise InstrIOError('Instrument did not set correctly the power')
        self.check_calibration()

    @instrument_property
    @secure_communication()
    def output(self):
        """Output state.

        """
        outputE = self.query('E?')
        outputr = self.query('r?')
        if outputE and outputr:
            outputE = outputE[0]
            outputr = outputr[0]
            if outputE == '1' and outputr == '1':
                return True
            if outputE == '0' and outputr == '0':
                return False
            else:
                mes = '''The synthHD is in an intermediate state,
                neither fully quiet, nor fully operational,
                received {} {}'''.format(outputE, outputr)
                raise InstrIOError(mes)
        else:
            mes = 'SynthHD signal generator did not return its output'
            raise InstrIOError(mes)

    @output.setter
    @secure_communication()
    def output(self, value):
        """Output setter method.

        """
        on = re.compile('on', re.IGNORECASE)
        off = re.compile('off', re.IGNORECASE)
        if on.match(value) or value == 1:
            self.write('E1r1')
            if not self.output:
                raise InstrIOError(cleandoc('''Instrument did not set correctly
                                        the output'''))
        elif off.match(value) or value == 0:
            self.write('E0r0')
            if self.output:
                raise InstrIOError(cleandoc('''Instrument did not set correctly
                                        the output'''))
        else:
            mess = fill(cleandoc('''The invalid value {} was sent to
                        switch_on_off method''').format(value), 80)
            raise VisaTypeError(mess)
        self.check_calibration()

    def check_calibration(self):
        """Validate that the source is calibrated and phase locked.

        Raises
        ------
        InstrIOError: raised if the source is not calibrated or phase locked.

        """
        result = self.query('V')
        if not result or not int(result):
            mes = 'SynthHD did not calibrate freq or power properly'
            raise InstrIOError(mes)
        if self.output:
            pll_status = self.query('p')
            if not pll_status or not int(pll_status):
                mes = 'SynthHD did not phase lock'
                raise InstrIOError(mes)
