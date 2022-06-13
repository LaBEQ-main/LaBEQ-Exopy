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