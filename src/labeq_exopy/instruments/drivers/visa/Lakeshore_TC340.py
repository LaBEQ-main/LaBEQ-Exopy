# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Authors - Kathryn Evancho, LaBEQ / Sardashti Research Group, Clemson University
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------

"""Drivers for Lakeshore 340 Temperature Controller using VISA library.

"""
from ..driver_tools import (InstrIOError, secure_communication, instrument_property)
from ..visa_tools import VisaInstrument


class LakeshoreTC340(VisaInstrument):
    """Lakeshore 340 Temperature Controller. """

    def open_connection(self, **para):
        """Open the connection to the instr using the `connection_str`.

        """
        super(LakeshoreTC340, self).open_connection(**para)
        self.write_termination = '\n'
        self.read_termination = '\n'

    def set_loop_limits(self, val):
        """CLIMIT handels all limit settings for loop 1 or 2:
            setpoint limit/loop cutoff, max positive change in output, max negative change in output, 
            max current, max heater range """

        self.write()

    def set_heater_range(self, ):
        "Sets Heater Range to 'off' or one of the output values"

    def set_control_channel(self, ):
        "Sets the control channel to input A or B"
    
    def configure_control(self, ):
        """CSET configures the control loop parameters of loop 1 or 2:
            control channel, setpoint units, on/off, on/off on startup"""
    
    def measure_temperature(self, ):
        """ Returns the temperature reading the selected input in kelvin """

        self.write()

    def set_PID(self, val):
        """ Sets the PID values of the selected loop or sets to AUTO PID"""

        self.write()

    def set_mout(self, val):
        """Sets the manual output percentage """

        self.write()
    
    def set_setpoint(self, val):
        """sets the heater setpoint """

        self.write()
    
    def input_settings(self, val):
        """The INTYPE command controlls all of the input settings for A or B: 
            Diode type, Units, Coefficient, Excitation, Range"""

        self.write()

    def set_input_curve(self, val):
        """sets the diode curve """

        self.write()
