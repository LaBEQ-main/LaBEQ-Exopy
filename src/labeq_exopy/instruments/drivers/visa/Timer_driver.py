# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Authors - Frank Duffy, LaBEQ / Sardashti Research Group, Clemson University
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------

"""Drivers for Oxford MercuryiTC temperature controller using VISA library.

"""
from ..driver_tools import (InstrIOError, secure_communication, instrument_property)
from ..visa_tools import VisaInstrument
import time

class Timer(VisaInstrument):

    start_time = 0
    elapsed_time = 0

    def open_connection(self, **para):
        pass

    def initiate_timer(self):
        #set now as start time, t=0
        t = self.start_time = time.time()
        return t

    def get_elapsed_time(self):
        #return time elapsed since start time
        t = self.elapsed_time = time.time() - self.start_time
        t = round(t, 3)
        return t

    def get_time_stamp(self):
        #return time stamp
        tstamp = time.time()
        return tstamp

    

