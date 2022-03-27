# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyHqcLegacy Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Drivers for Anapico SignalGenerator using VISA library.

"""
import re
from textwrap import fill
from inspect import cleandoc

from visa import VisaTypeError

from ..driver_tools import (InstrIOError, instrument_property,
                            secure_communication)
from ..visa_tools import VisaInstrument


class Anapico(VisaInstrument):
    """
    Generic driver for Anapico Signal Generators,
    using the VISA library.

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

        super(Anapico, self).__init__(connection_info,
                                      caching_allowed,
                                      caching_permissions,
                                      auto_open)
        self.frequency_unit = 'GHz'
        self.write_termination = '\n'
        self.read_termination = '\n'
# The next line sets the timeout before reconnection to 0. This is available
# since firmware version 0.4.106 and avoids the Anapico generator to freeze
# upon unproperly closed connections (for instance if exopy crashes)
# no need to turn the generator OFF and ON with this line
# here if the explanation from the support team at Anapico:
# I added a reconnect timeout option. It allows to reconnect to an
# inactive link that has never been closed. The timeout defines how long
# the user must wait until the link is considered inactive and reconnect is
# enabled. The default timeout is infinite, meaning no reconnect possible at
# all so it behaves like earlier firmare. In this application the timeout can
# be set to zero so reconnect is always possible immediately.
#
# The command is "SYST:COMM:VXI:RTMO <x>", where "<x>" is the reconnect timeout
# in seconds or "INF" for infinite. If they need to reuse to an unclosed link,
# they should always send "SYST:COMM:VXI:RTMO 0" immediately after opening a
# connection.
        self.write("SYST:COMM:VXI:RTMO 0")

    @instrument_property
    @secure_communication()
    def frequency(self):
        """Frequency of the output signal.

        """
        freq = self.query('FREQ?')
        if freq:
            return float(freq)
        else:
            raise InstrIOError

    @frequency.setter
    @secure_communication()
    def frequency(self, value):
        """Frequency setter method.

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
            elif unit == 'KHz':
                result /= 1e3
            if abs(result - value) > 1e-12:
                mes = 'Instrument did not set correctly the frequency.'
                raise InstrIOError(mes)

    @instrument_property
    @secure_communication()
    def power(self):
        """Power of the output signal.

        """
        power = self.query('POWER?')
        if power:
            return float(power)
        else:
            raise InstrIOError

    @power.setter
    @secure_communication()
    def power(self, value):
        """Power setter method.

        """
        self.write('POWER {}'.format(value))
        result = float(self.query('POWER?'))
        if abs(result - value) > 1e-4:
            raise InstrIOError('Instrument did not set correctly the power')

    @instrument_property
    @secure_communication()
    def output(self):
        """Output state of the source.

        """
        output = self.query(':OUTP?')
        if output:
            return bool(int(output))
        else:
            mes = 'Anapico signal generator did not return its output'
            raise InstrIOError(mes)

    @output.setter
    @secure_communication()
    def output(self, value):
        """Output setter method.

        """
        on = re.compile('on', re.IGNORECASE)
        off = re.compile('off', re.IGNORECASE)
        if on.match(value) or value == 1:
            self.write(':OUTPUT ON')
            if self.query(':OUTPUT?') != '1':
                raise InstrIOError(cleandoc('''Instrument did not set correctly
                                        the output'''))
        elif off.match(value) or value == 0:
            self.write(':OUTPUT OFF')
            if self.query(':OUTPUT?') != '0':
                raise InstrIOError(cleandoc('''Instrument did not set correctly
                                        the output'''))
        else:
            mess = fill(cleandoc('''The invalid value {} was sent to
                        switch_on_off method''').format(value), 80)
            raise VisaTypeError(mess)

    @instrument_property
    @secure_communication()
    def pm_state(self):
        """Pulse modulation getter method

        """
        pm_state = self.query('SOURce:PULM:STATE?')
        if pm_state:
            return bool(pm_state)
        else:
            mes = 'Anapico signal generator did not return its pulse modulation state'
            raise InstrIOError(mes)

    @pm_state.setter
    @secure_communication()
    def pm_state(self, value):
        """Pulse modulation setter method.

        """
        # TODO: write checks
        self.write('SOURce:PULM:SOURce EXT')
        self.write('SOURce:PULM:POLarity NORMal')
        self.write('SOURce:PULM:TRIGger:EXTernal:IMPedance G50')
        on = re.compile('on', re.IGNORECASE)
        off = re.compile('off', re.IGNORECASE)
        if on.match(value) or value == 1:
            self.write('SOURce:PULM:STATE ON')
            if self.query('SOURce:PULM:STATE?') != '1':
                raise InstrIOError(cleandoc('''Instrument did not set correctly
                                        the pulse modulation state'''))
        elif off.match(value) or value == 0:
            self.write('SOURce:PULM:STATE OFF')
            if self.query('SOURce:PULM:STATE?') != '0':
                raise InstrIOError(cleandoc('''Instrument did not set correctly
                                        the pulse modulation state'''))
        else:
            mess = fill(cleandoc('''The invalid value {} was sent to
                        switch_on_off method''').format(value), 80)
            raise VisaTypeError(mess)


class AnapicoMulti(Anapico):
    """
    Generic driver for multi-channel Anapico Signal Generators,
    using the VISA library.

    Parameters
    ----------
    see the `VisaInstrument` parameters

    Attributes
    ----------
    channel: int
        Channel currently selected
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

    @instrument_property
    @secure_communication()
    def channel(self):
        """Currently selected channel

        """
        channel = self.query('SOURce:SEL?')
        if channel:
            return int(channel)
        else:
            raise InstrIOError

    @channel.setter
    @secure_communication()
    def channel(self, channel):
        """Current channel setter method

        """
        self.write('SOURce:SEL {}'.format(channel))
        result = int(self.query('SOURce:SEL?'))
        if result and channel != result:
            msg = 'Instrument could not select channel {}'
            raise InstrIOError(msg.format(channel))
