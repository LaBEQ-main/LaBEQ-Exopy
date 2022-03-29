# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyHqcLegacy Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Drivers for keysight multimeters using VISA library.

"""
from ..driver_tools import (InstrIOError, secure_communication)
from ..visa_tools import VisaInstrument


class Agilent34410A(VisaInstrument):
    """
    Driver for an Agilent 34410A multimeter, using the VISA library.

    This driver does not give access to all the functionnality of the
    instrument but you can extend it if needed. See the documentation of
    the `driver_tools` module for more details about writing instruments
    drivers.

    Parameters
    ----------
    see the `VisaInstrument` parameters in the `driver_tools` module

    Methods
    -------
    read_voltage_dc(mes_range = 'DEF', mes_resolution = 'DEF')
        Return the DC voltage measured by the instrument
    read_voltage_ac(mes_range = 'DEF', mes_resolution = 'DEF')
        Return the AC voltage measured by the instrument
    read_resistance(mes_range = 'DEF', mes_resolution = 'DEF')
        Return the resistance measured by the instrument
    read_current_dc(mes_range = 'DEF', mes_resolution = 'DEF')
        Return the DC current measured by the instrument
    read_current_ac(mes_range = 'DEF', mes_resolution = 'DEF')
        Return the AC current measured by the instrument

    Notes
    -----
    This driver has been written for the Agilent 34410A but might work for
    other models using the same SCPI commands.

    """
    def open_connection(self, **para):
        """Open the connection to the instr using the `connection_str`.

        """
        super(Agilent34410A, self).open_connection(**para)
        self.write_termination = '\n'
        self.read_termination = '\n'

    @secure_communication()
    def read_voltage_dc(self, mes_range='DEF', mes_resolution='DEF'):
        """Return the DC voltage measured by the instrument
        """
        instruction = "MEASure:VOLTage:DC? {},{}"
        value = self.query(instruction.format(mes_range, mes_resolution))
        if value:
            return float(value)
        else:
            raise InstrIOError('DC voltage measure failed')

    @secure_communication()
    def read_voltage_ac(self, mes_range='DEF', mes_resolution='DEF'):
        """Return the AC voltage measured by the instrument
        """
        instruction = "MEASure:VOLTage:AC? {},{}"
        value = self.query(instruction.format(mes_range, mes_resolution))
        if value:
            return float(value)
        else:
            raise InstrIOError('AC voltage measure failed')

    @secure_communication()
    def read_resistance(self, mes_range='DEF', mes_resolution='DEF'):
        """Return the resistance measured by the instrument
        """
        instruction = "MEASure:RESistance? {},{}"
        value = self.query(instruction.format(mes_range,
                                                       mes_resolution))
        if value:
            return float(value)
        else:
            raise InstrIOError('Resistance measure failed')

    @secure_communication()
    def read_current_dc(self, mes_range='DEF', mes_resolution='DEF'):
        """Return the DC current measured by the instrument
        """
        instruction = "MEASure:CURRent:DC? {},{}"
        value = self.query(instruction.format(mes_range, mes_resolution))
        if value:
            return float(value)
        else:
            raise InstrIOError('DC current measure failed')

    @secure_communication()
    def read_current_ac(self, mes_range='DEF', mes_resolution='DEF'):
        """Return the AC current measured by the instrument
        """
        instruction = "MEASure:CURRent:AC? {},{}"
        value = self.query(instruction.format(mes_range,  mes_resolution))
        if value:
            return float(value)
        else:
            raise InstrIOError('AC current measure failed')
