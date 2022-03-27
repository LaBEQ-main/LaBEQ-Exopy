# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyHqcLegacy Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Drivers for the BILT rack BN100 with BE2100 cards using VISA library.

"""
import re
import time
from textwrap import fill
from inspect import cleandoc
from threading import Lock
from contextlib import contextmanager

import numpy as np
from visa import VisaTypeError
from pyvisa.errors import InvalidSession, VisaIOError

from ..driver_tools import (BaseInstrument, InstrIOError, secure_communication,
                            instrument_property)
from ..visa_tools import VisaInstrument


class TinyBiltChannel(BaseInstrument):

    secure_com_except = (InvalidSession, InstrIOError, VisaIOError)

    def __init__(self, TB, channel_num, caching_allowed=True,
                 caching_permissions={}, header_format='BE2101'):
        super(TinyBiltChannel, self).__init__(None, caching_allowed,
                                              caching_permissions)
        self._TB = TB
        self._channel = channel_num
        if header_format == 'BE2141':
            self._header = 'i{};c{};'.format(*channel_num)
        else:
            self._header = 'i{};'.format(channel_num[0])

    def reopen_connection(self):

        self._TB.reopen_connection()

    @contextmanager
    def secure(self):
        """ Lock acquire and release method

        """
        i = 0
        while not self._TB.lock.acquire():
            time.sleep(0.1)
            i += 1
            if i > 50:
                raise InstrIOError
        try:
            yield
        finally:
            self._TB.lock.release()

    @instrument_property
    @secure_communication()
    def output(self):
        """ Output getter method

        """

        with self.secure():
            output = self._TB.query(self._header + 'OUTP?')
            if output == '1':
                return 'ON'
            elif output == '0':
                return 'OFF'
            else:
                mes = 'TinyBilt did not return its output'
                raise InstrIOError(mes)


    @output.setter
    @secure_communication()
    def output(self, value):
        """Output setter method. 'ON', 'OFF'
        """
        with self.secure():
            on = re.compile('on', re.IGNORECASE)
            off = re.compile('off', re.IGNORECASE)
            if value == 1 or on.match(str(value)):
                self._TB.write(self._header + 'OUTP1')
                if self._TB.query(self._header + 'OUTP?') != '1':
                    raise InstrIOError(cleandoc('''Instrument did not set
                                                correctly the output'''))
            elif value == 0 or off.match(str(value)):
                self._TB.write(self._header + 'OUTP0')
                if self._TB.query(self._header + 'OUTP?') != '0':
                    raise InstrIOError(cleandoc('''Instrument did not set
                                                correctly the output'''))
            else:
                mess = fill(cleandoc('''The invalid value {} was sent to
                            switch_on_off method''').format(value), 80)
                raise VisaTypeError(mess)


    @instrument_property
    @secure_communication()
    def big_volt_range(self):
        """Voltage range getter method. Two values possible :
        big range = 12V and small range = 1.2V
        """
        with self.secure():
            voltage = self._TB.query(self._header + 'volt:rang?')
            if voltage:
                return float(voltage)
            else:
                raise InstrIOError

    @big_volt_range.setter
    @secure_communication()
    def big_volt_range(self, value):
        """Voltage range method. Two values possible :
        big range = 12V = 'True' or 1 and small range = 1.2V = 'False' or 0
        TinyBilt need to be turned off to change the voltage range
        """
        with self.secure():
            outp = self._TB.query(self._header + 'OUTP?')
            if outp == 1:
                raise InstrIOError(cleandoc('''TinyBilt need to be turned
                                                 off to change the voltage
                                                range'''))
            if value in ('True', 1):
                self._TB.write(self._header + 'volt:rang 12')
                result = self._TB.query(self._header + 'volt:rang?')
                if abs(float(result) - 12) > 10**-12:
                    mess = 'Instrument did not set correctly the range voltage'
                    raise InstrIOError(mess)
            elif value in ('False', 0):
                self._TB.write(self._header + 'volt:rang 1.2')
                result = self._TB.query(self._header + 'volt:rang?')
                if abs(float(result) - 1.2) > 10**-12:
                    raise InstrIOError(cleandoc('''Instrument did not set
                                                correctly the range
                                                voltage'''))
            else:
                raise ValueError(cleandoc('''Big range 12V = "True"
                                          or 1, small range 1.2V
                                          = "False" or 0'''))

    @instrument_property
    @secure_communication()
    def max_voltage(self):
        """max voltage getter method
        """
        with self.secure():
            maxV = self._TB.query(self._header + 'volt:sat:pos?')
            if maxV:
                return float(maxV)
            else:
                raise InstrIOError

    @max_voltage.setter
    @secure_communication()
    def max_voltage(self, value):
        """max voltage setter method
        """
        with self.secure():
            self._TB.write(self._header + 'volt:sat:pos {}'.format(value))
            maxiV = self._TB.query(self._header + 'volt:sat:pos?')
            if abs(float(maxiV) - value) > 10**-12:
                raise InstrIOError(cleandoc('''Instrument did not set
                                            correctly the maximum
                                            voltage'''))

    @instrument_property
    @secure_communication()
    def min_voltage(self):
        """min voltage getter method
        """
        with self.secure():
            minV = self._TB.query(self._header + 'volt:sat:neg?')
            if minV:
                return float(minV)
            else:
                raise InstrIOError

    @min_voltage.setter
    @secure_communication()
    def min_voltage(self, value):
        """min voltage setter method
        """
        with self.secure():
            self._TB.write(self._header + 'volt:sat:neg {}'.format(value))
            miniV = self._TB.query(self._header + 'volt:sat:neg?')
            if abs(float(miniV) - value) > 10**-12:
                raise InstrIOError(cleandoc('''Instrument did not set
                                            correctly the minimum
                                            voltage'''))

    @instrument_property
    @secure_communication()
    def voltage(self):
        """output value getter method
        """
        with self.secure():
            outp_val = self._TB.query(self._header + 'Volt?')
            if outp_val:
                return float(outp_val)
            else:
                raise InstrIOError

    @voltage.setter
    @secure_communication()
    def voltage(self, value):
        """Output value setter method

        """
        with self.secure():
            self._TB.write(self._header + 'Volt {}'.format(value))
            self._TB.write(self._header + 'trig:input:init')
            result = round(float(self._TB.query(self._header + 'Volt?')), 5)
            if abs(result - value) > 1e-12:
                raise InstrIOError(cleandoc('''Instrument did not set
                                            correctly the output
                                            value'''))

    @secure_communication()
    def smooth_change(self, volt_destination, volt_step, time_step):
        """ Set a ramp from the present voltage
            to the volt_destination by step of volt_step
            with time of time_step between each step
        """
        with self.secure():
            present_voltage = round(float(self._TB.query
                                          (self._header + 'Volt?')), 5)
            while abs(round(present_voltage - volt_destination,
                            5)) >= volt_step:
                time.sleep(time_step)
                self._TB.write(self._header + 'volt {}'
                               .format(present_voltage))
                present_voltage = round(present_voltage + volt_step *
                                        np.sign(volt_destination -
                                                present_voltage), 5)
            self._TB.write(self._header + 'volt {}'
                           .format(volt_destination))


class TinyBilt(VisaInstrument):
    """
    """
    caching_permissions = {'defined_channels': True}
    secure_com_except = (InvalidSession, InstrIOError, VisaIOError)

    def __init__(self, connection_info, caching_allowed=True,
                 caching_permissions={}, auto_open=True):
        super(TinyBilt, self).__init__(connection_info, caching_allowed,
                                       caching_permissions, auto_open)
        self.channels = {}
        self.lock = Lock()

    def open_connection(self, **para):
        """Open the connection to the instr using the `connection_str`
        """
        super(TinyBilt, self).open_connection(**para)
        self.write_termination = '\n'
        self.read_termination = '\n'

    def get_channel(self, num):
        """num is a tuple containing (module_number,channel_number)
        """
        defined = self.defined_channels
        if num not in defined:
            msg = 'No channel {}, only channels {} exist'
            raise KeyError(msg.format(num, defined))

        hf = ('BE2101' if num[1] == 1 and (num[0], 2) not in defined
              else 'BE2141')

        if num in self.channels:
            return self.channels[num]
        else:
            channel = TinyBiltChannel(self, num, header_format=hf)
            self.channels[num] = channel
            return channel

    @instrument_property
    @secure_communication()
    def defined_channels(self):
        """defined_channels is a list of tuple with format (module_number,
                                                                channel_number)
        """
        modules = self.query('I:L?')
        if modules:
            defined_modules = np.array([s.split(',')
                                            for s in modules.split(';')],
                                            dtype=np.uint)
            defined_channels = []
            for i in defined_modules[:,0].tolist():
                if defined_modules[i-1,1]==2141:
                    defined_channels.extend([(i,1), (i,2), (i,3), (i,4)])
                elif defined_modules[i-1,1]==2101:
                    defined_channels.append((i,1))
                else:
                    raise InstrIOError(cleandoc('''Driver not written for
                                                    this type of module'''))
            return defined_channels

        else:
            raise InstrIOError(cleandoc('''Instrument did not return
                                            the defined channels'''))
