# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Authors - Frank Duffy, LaBEQ / Sardashti Research Group, Clemson University
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------

"""Drivers for NF LI5650 lock-in amplifier using VISA library.

"""
from ..driver_tools import (InstrIOError, secure_communication, instrument_property)
from ..visa_tools import VisaInstrument


class LI5650(VisaInstrument):
    """NF LI5650 lock-in amplifier. """

    def open_connection(self, **para):
        """Open the connection to the instr using the `connection_str`.

        """
        super(LI5650, self).open_connection(**para)
        self.write_termination = '\n'
        self.read_termination = '\n'

    def set_sens_mode(self, mode):
        """ set sensitivity mode """
        
        self.write('SENS:VOLT:AC:RANG:AUTO ' + str(mode))

    def set_dynres(self, mode):
        """ set dynamic reserve low/med/high """

        self.write('SENS:DRES ' + str(mode))

    def set_sensitivity(self, val):
        """ set sensitivity range 10E-9 to 1, 1-2-5 sequence, unit Vrms """

        self.write('SENS:VOLT:AC:RANG:UPP ' + str(val))

    def set_tc(self, val):
        """set time constant """

        self.write('SENS:FILT:LPAS:TCON ' + str(val))
    
    def set_tc_slope(self, val):
        """set time constant """

        self.write('SENS:FILT:LPAS:SLOP ' + str(val))


