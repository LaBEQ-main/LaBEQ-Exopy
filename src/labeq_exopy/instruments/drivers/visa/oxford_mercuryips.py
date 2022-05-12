# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Authors - Frank Duffy
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------

"""Drivers for oxford ips magnet supply using VISA library.

"""
from ..driver_tools import (InstrIOError, secure_communication, instrument_property)
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
    def read_field_potential(self):
        """ return the potential field strength value"""
    
        resp = self.query('READ:DEV:GRPZ:PSU:SIG:FLD?')

        #query will return string STAT:DEV:GRPZ:PSU:SIG:FLD:0.0000T. We only want the last value as a float.
        value = f'{resp}'.split(':')[-1]
        value = value.replace('T','')

        if value:
            return float(value)
        else:
            raise InstrIOError('MercuryiPS: Current field capacity reading failed')
    
    @secure_communication()
    def read_field_actual(self):
        """ return the actual field strength value"""
    
        resp = self.query('READ:DEV:GRPZ:PSU:SIG:PFLD?')

        #query will return string STAT:DEV:GRPZ:PSU:SIG:FLD:0.0000T. We only want the last value as a float.
        value = f'{resp}'.split(':')[-1]
        value = value.replace('T','')

        if value:
            return float(value)
        else:
            raise InstrIOError('MercuryiPS: Current field strength reading failed')

    @secure_communication()
    def ramp_mag_field(self, setpoint):
        """ramp the magnetic field to the set point"""

        # send the query and obtain the status string
        resp = self.query('READ:DEV:GRPZ:PSU:SIG:SWHT?')

        #isolate status string "OFF" or "ON"
        value = f'{resp}'.split(':')[-1].strip()

        #swh_status = value
        swh_status = self.read_switch_status()
        print(f'switch status: {swh_status}')

        if swh_status == "OFF":
            raise InstrIOError('MercuryiPS: Switch heater is off. Commanded current will not flow through magnet coils.')
        elif swh_status == "ON":
            if setpoint <= 0.1:
                self.query('SET:DEV:GRPZ:PSU:SIG:FSET:' + str(setpoint))
                self.query('SET:DEV:GRPZ:PSU:ACTN:RTOS')
            else:
                raise InstrIOError('MercuryiPS: Field strength set point greater than 0.1T. Reduce and try again.')
        else:
            raise InstrIOError('MercuryiPS: Failed to read switch status')

    @secure_communication()
    def read_switch_status(self):
        """read the switch heater status"""

        # send the query and obtain the status string
        resp = self.query('READ:DEV:GRPZ:PSU:SIG:SWHT?')

        #isolate status string "OFF" or "ON"
        value = f'{resp}'.split(':')[-1].strip()

        if value == "OFF" or "ON":
            return value 
        else:
            raise InstrIOError('MercuryiPS: Failed to read switch status')