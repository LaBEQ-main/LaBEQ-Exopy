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
    
    def __init__(self, connection_info, caching_allowed=True,
                caching_permissions={}):
        super(ZM2376, self).__init__(connection_info, caching_allowed,
                caching_permissions)
        self.write_termination = '\n'
        self.read_termination = '\n'

        # get current pri and sec measurement parameters
        self.curr_pri = self.query('CALC1:FORM?')
        self.curr_sec = self.query('CALC2:FORM?')

        print(self.curr_pri)

    def open_connection(self, **para):
        """Open the connection to the instr using the `connection_str`.

        """
        super(ZM2376, self).open_connection(**para)
    
    def set_frequency(self, val):
        """ set the source frequency 
        
        """
        self.write('SOUR:FREQ ' + str(val))

    def set_voltage(self, val):
        """ set the source voltage level

        """
        self.write('SOUR:VOLT:LEV ' + str(val))

    def fetch_measurements(self, params):
        """ fetch the latest measurements

        """
        # gather requested parameters
        req_pri = params[0]
        req_sec = params[1]

        if self.curr_pri != req_pri or self.curr_sec != req_sec:
            self.set_parameters(req_pri, req_sec)

        resp = self.query('FETC?').split(",")

        pri = resp[1]
        sec = resp[2]

        return pri, sec

    def set_parameters(self, pri, sec):
        """ set the primary and secondary measurement parameters and update driver attributes """

        self.write('CALC1:FORM '+ pri)
        self.curr_pri = pri

        self.write('CALC2:FORM '+ sec)
        self.curr_sec = sec




