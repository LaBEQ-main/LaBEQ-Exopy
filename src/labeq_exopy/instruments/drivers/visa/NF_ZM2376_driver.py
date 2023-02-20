# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Authors - Frank Duffy, LaBEQ / Sardashti Research Group, Clemson University
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------

from tracemalloc import reset_peak
from ..driver_tools import (InstrIOError, secure_communication, instrument_property)
from ..visa_tools import VisaInstrument

class ZM2376(VisaInstrument):
    """Driver for NF ZM2376 LCR Meter.

    """

    def open_connection(self, **para):
        """Open the connection to the instr using the `connection_str`.

        """
        super(ZM2376, self).open_connection(**para)
        self.write_termination = '\n'
        self.read_termination = '\n'
    
    def set_frequency(self, val):
        """ set the source frequency 
        
        """
        self.write('SOUR:FREQ ' + str(val))

    def set_voltage(self, val)
        """ set the source voltage level

        """
        self.write('SOUR:VOLT:LEV ' + str(val))

    def fetch_measurements(self, val)
        """ fetch the latest measurements

        """
        resp = self.query('FETC?').split(",")

        pri = resp[1]
        sec = resp[2]

        return pri, sec
