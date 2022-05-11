# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------
"""Drivers for oxford ips magnet supply using VISA library.

"""
from ..driver_tools import (InstrIOError, secure_communication)
from ..visa_tools import VisaInstrument

class MercuryiPS(VisaInstrument):
    """Driver for the MercuryiPS superconducting magnet power supply 
    manufactured by Oxford Instruments.

    Parameters
    ----------
    see the `VisaInstrument` parameters in the `driver_tools` module

    Methods
    -------
    read_x()
        Return the x quadrature measured by the instrument

    Notes

    -----

    """

    def open_connection(self, **para):
        """Open the connection to the instr using the `connection_str`.

        """
        super(MercuryiPS, self).open_connection(**para)
        self.write_termination = '\n'
        self.read_termination = '\n'

    @secure_communication()
    def read_current_field(self):
        """ return the current field strength value"""
    
        value = self.query('READ:DEV:GRPZ:PSU:SIG:FLD?')
        if value:
            return float(value)
        else:
            raise InstrIOError('MercuryiPS: Current field strength reading failed')