# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Authors - Frank Duffy, LaBEQ / Sardashti Research Group, Clemson University
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------

"""Drivers for oxford ips magnet supply using VISA library.

"""
from tracemalloc import reset_peak
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
    def read_supply_field(self):
        """ return the supply field strength value"""
    
        resp = self.query('READ:DEV:GRPZ:PSU:SIG:FLD?')

        #query will return string STAT:DEV:GRPZ:PSU:SIG:FLD:0.0000T. We only want the last value as a float.
        value = f'{resp}'.split(':')[-1]
        value = value.replace('T','')

        if value:
            return float(value)
        else:
            raise InstrIOError('MercuryiPS: Supply field strength reading failed')
    
    @secure_communication()
    def read_supply_field_rate(self):
        """ return the supply field rate value"""
    
        resp = self.query('READ:DEV:GRPZ:PSU:SIG:RFLD?')

        #query will return string STAT:DEV:GRPZ:PSU:SIG:RFLD:0.0000T/min. We only want the last value as a float.
        value = f'{resp}'.split(':')[-1]
        value = value.replace('T/min','')

        if value:
            return float(value)
        else:
            raise InstrIOError('MercuryiPS: Supply field rate reading failed')
    
    @secure_communication()
    def read_magnet_field(self):
        """ return the magnetic field strength produced by the energized coils value"""
    
        resp = self.query('READ:DEV:GRPZ:PSU:SIG:PFLD?')

        #query will return string STAT:DEV:GRPZ:PSU:SIG:FLD:0.0000T. We only want the last value as a float.
        value = f'{resp}'.split(':')[-1]
        value = value.replace('T','')

        if value:
            return float(value)
        else:
            raise InstrIOError('MercuryiPS: Magnetic field strength reading failed')
    
    @secure_communication()
    def read_supply_voltage(self):
        """ return the supply voltage reading"""
    
        resp = self.query('READ:DEV:GRPZ:PSU:SIG:VOLT?')

        #query will return string STAT:DEV:GRPZ:PSU:SIG:VOLT:0.0000V. We only want the last value as a float.
        value = f'{resp}'.split(':')[-1]
        value = value.replace('V','')

        if value:
            return float(value)
        else:
            raise InstrIOError('MercuryiPS: Supply voltage reading failed')
    
    @secure_communication()
    def read_supply_current(self):
        """ return the supply current reading"""
    
        resp = self.query('READ:DEV:GRPZ:PSU:SIG:CURR?')

        #query will return string STAT:DEV:GRPZ:PSU:SIG:CURR:0.0000A. We only want the last value as a float.
        value = f'{resp}'.split(':')[-1]
        value = value.replace('A','')

        if value:
            return float(value)
        else:
            raise InstrIOError('MercuryiPS: Supply current reading failed')

    @secure_communication()
    def read_supply_current_rate(self):
        """ return the supply current rate reading"""
    
        resp = self.query('READ:DEV:GRPZ:PSU:SIG:RCUR?')

        #query will return string STAT:DEV:GRPZ:PSU:SIG:RCUR:0.0000A/min. We only want the last value as a float.
        value = f'{resp}'.split(':')[-1]
        value = value.replace('A/min','')

        if value:
            return float(value)
        else:
            raise InstrIOError('MercuryiPS: Supply current rate reading failed')

    @secure_communication()
    def read_magnet_current(self):
        """ return the current circulating in the magnet coils"""
    
        resp = self.query('READ:DEV:GRPZ:PSU:SIG:PCUR?')

        #query will return string STAT:DEV:GRPZ:PSU:SIG:PCUR:0.0000A. We only want the last value as a float.
        value = f'{resp}'.split(':')[-1]
        value = value.replace('A','')

        if value:
            return float(value)
        else:
            raise InstrIOError('MercuryiPS: Magnet current reading failed')

    @secure_communication()
    def read_target_current(self):
        """ return the target current reading"""
    
        resp = self.query('READ:DEV:GRPZ:PSU:SIG:CSET?')

        #query will return string STAT:DEV:GRPZ:PSU:SIG:CSET:0.0000A. We only want the last value as a float.
        value = f'{resp}'.split(':')[-1]
        value = value.replace('A','')

        if value:
            return float(value)
        else:
            raise InstrIOError('MercuryiPS: Target current reading failed')
    
    @secure_communication()
    def set_target_current(self, target):
        """ set the target current """
    
        self.query('SET:DEV:GRPZ:PSU:SIG:CSET:' + str(target))

    @secure_communication()
    def read_target_current_rate(self):
        """ return the target current rate reading"""
    
        resp = self.query('READ:DEV:GRPZ:PSU:SIG:RCST?')

        #query will return string STAT:DEV:GRPZ:PSU:SIG:RCST:0.0000A/m. We only want the last value as a float.
        value = f'{resp}'.split(':')[-1]
        value = value.replace('A/m','')

        if value:
            return float(value)
        else:
            raise InstrIOError('MercuryiPS: Target current rate reading failed')
    
    @secure_communication()
    def set_target_current_rate(self, target):
        """ set the target current rate """
    
        self.query('SET:DEV:GRPZ:PSU:SIG:RCST:' + str(target))
    
    @secure_communication()
    def read_target_field(self):
        """ return the target field """
    
        resp = self.query('READ:DEV:GRPZ:PSU:SIG:FSET?')

        #query will return string STAT:DEV:GRPZ:PSU:SIG:FSET:0.0000T. We only want the last value as a float.
        value = f'{resp}'.split(':')[-1]
        value = value.replace('T','')

        if value:
            return float(value)
        else:
            raise InstrIOError('MercuryiPS: Target field reading failed')
    
    @secure_communication()
    def set_target_field(self, target):
        """ set the target field """
    
        self.query('SET:DEV:GRPZ:PSU:SIG:FSET:' + str(target))
    
    @secure_communication()
    def read_target_field_rate(self):
        """ return the target field rate """
    
        resp = self.query('READ:DEV:GRPZ:PSU:SIG:RFST?')

        #query will return string STAT:DEV:GRPZ:PSU:SIG:RFST:0.0000T/m. We only want the last value as a float.
        value = f'{resp}'.split(':')[-1]
        value = value.replace('T/m','')

        if value:
            return float(value)
        else:
            raise InstrIOError('MercuryiPS: Target field rate reading failed')

    @secure_communication()
    def set_target_field_rate(self, target):
        """ set the target field rate """
    
        self.query('SET:DEV:GRPZ:PSU:SIG:RFST:' + str(target))

    @secure_communication()
    def ramp_to_target(self):
        """ramp the magnetic field to the target value """

        #set cap on field change amount
        intrvl_cap = 0.1

        #get target to check against safety cap
        target = self.read_target_field()

        #get current fld to check against safety cap
        current = self.read_supply_field()

        #calculate proposed field change
        field_delta = abs(target - current)

        #swh_status = value
        swh_status = self.read_switch_status()
        print(f'switch status: {swh_status}')

        if swh_status == "OFF":
            raise InstrIOError('MercuryiPS: Switch heater is off. Commanded current will not flow through magnet coils.')
        elif swh_status == "ON":
            if field_delta <= intrvl_cap:
                self.query('SET:DEV:GRPZ:PSU:ACTN:RTOS')
            else:
                raise InstrIOError(f'MercuryiPS: Field strength set point greater than 0.1T. Reduce and try again.')
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
    
    @secure_communication()
    def read_sensor(self, device_name, value):
        """read the switch heater status"""

        print(device_name)
        print(value)
        #get address of device
        dev_addr = device_name.split('_')[1]

        print(dev_addr)

        msg = f'READ:DEV:{dev_addr}:TEMP:SIG:{value}?'
        print(msg)

        # send the query and obtain the status string
        resp = self.query(msg)
        print(resp)

        #query will return string STAT:DEV:{dev_addr}:TEMP:SIG:{value}:#.####K. We only want the last value as a float.
        value = f'{resp}'.split(':')[-1]

        if value == 'TEMP':
            value = value.replace('K','')
        elif value == "SLOP":
            value = value.replace('R/K','')
        elif value == "VOLT":
            value = value.replace('mV','')
        elif value == "RES":
            value = value.replace('R','')
        elif value == "SLOP":
            value = value.replace('R/K','')
        elif value == "CURR":                   #currently not readable, likely due to greek letter mu for micro. ascii cant decode
            value = value.replace('microA','')
        elif value == "POWR":                   #currently not readable, likely due to greek letter mu for micro. ascii cant decode
            value = value.replace('microW','')

        return value 