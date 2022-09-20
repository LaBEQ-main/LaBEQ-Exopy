# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Authors - Frank Duffy, LaBEQ / Sardashti Research Group, Clemson University
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------

"""Drivers for Oxford HelioxVT temperature controller using VISA library.

"""
from ..driver_tools import (InstrIOError, secure_communication, instrument_property)
from ..visa_tools import VisaInstrument


class HelioxVT(VisaInstrument):
    """Driver for the MercuryiTC temperature controller 
    manufactured by Oxford Instruments. """

    def open_connection(self, **para):
        """Open the connection to the instr using the `connection_str`.

        """
        super(HelioxVT, self).open_connection(**para)
        self.write_termination = '\n'
        self.read_termination = '\n'

    def read_VTI_temp(self):
        """
            read vti temp
        """

        resp = self.query('READ:DEV:DB6.T1:TEMP:SIG:TEMP?')
        value = f'{resp}'.split(':')[-1]
        value = value.replace('K','')

        if value:
            return float(value)
        else:
            raise InstrIOError('HelioxVT: VTI temp reading failed')
    
    def set_VTI_temp(self, setpoint):
        """
            set vti temp
        """

        resp = self.query(f'SET:DEV:DB6.T1:TEMP:LOOP:TSET:'+ str(setpoint))
        value = f'{resp}'.split(':')[-1]

        if value != "VALID":
            raise InstrIOError('HelioxVT: VTI temp set failed')

    def read_VTI_pres(self):
        """
            read vti pressure
        """

        resp = self.query('READ:DEV:DB3.P1:PRES:SIG:PRES?')
        value = f'{resp}'.split(':')[-1]
        value = value.replace('mB','')

        if value:
            return float(value)
        else:
            raise InstrIOError('HelioxVT: VTI pressure reading failed')

    def set_VTI_pres(self, setpoint):
        """
            set vti pres
        """

        resp = self.query(f'SET:DEV:DB3.P1:TEMP:LOOP:TSET:'+ str(setpoint))
        value = f'{resp}'.split(':')[-1]

        if value != "VALID":
            raise InstrIOError('HelioxVT: VTI pressure set failed')
    
    def read_VTI_valv_perc(self):
        """
            read vti needle valve percentage
        """

        resp = self.query('READ:DEV:DB4.G1:AUX:SIG:PERC?')
        value = f'{resp}'.split(':')[-1]
        value = value.replace('%','')

        if value:
            return float(value)
        else:
            raise InstrIOError('HelioxVT: VTI needle valve percentage reading failed')

    def read_He3pot_temp(self):
        """
            read probe temp
        """

        resp = self.query('READ:DEV:HelioxX:HEL:SIG:TEMP')
        value = f'{resp}'.split(':')[-1]
        value = value.replace('K','')

        if value:
            return float(value)
        else:
            raise InstrIOError('HelioxVT: He3 pot temp reading failed')

    def set_He3pot_temp(self, setpoint):
        """
            set probe temp
        """

        resp = self.query(f'SET:DEV:HelioxX:HEL:TSET:'+ str(setpoint))
        value = f'{resp}'.split(':')[-1]

        if value != "VALID":
            raise InstrIOError('HelioxVT: He3 pot set temperature failed')


   
