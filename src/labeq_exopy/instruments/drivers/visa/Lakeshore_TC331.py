# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Authors - Matthew Everette, LaBEQ / Sardashti Research Group, Clemson University
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------

from ..driver_tools import InstrIOError
from ..visa_tools import VisaInstrument


class LakeshoreTC331(VisaInstrument):
    """Driver for LakeShore 331 Temperature Controller, using the VISA library"""

    def open_connection(self, **para):
        super().open_connection(**para)
        self.write_termination = "\n"
        self.read_termination = "\n"

    def set_heater_range(self, range):
        """Sets the heater range"""

        self.write(f"RANGE {range}")
        print(f"setting heater range to {range}")

    def set_loop_control_parameters(
        self, loop, input, units, powerup_enable, heater_output_display
    ):
        """Configures a control loop's parameters:
        control input channel, setpoint units, on/off on startup, heater output display
        """

        self.write(
            f"CSET {loop},{input},{units},{powerup_enable},{heater_output_display}"
        )
        print("setting the control settings")

    def get_input_temperature(self, input):
        """Gets the temperature of an input in Kelvin"""

        status = int(self.query(f"RDGST? {input}"))

        if status == 0:
            return int(self.query(f"KRDG? {input}"))
        elif status & (1 << 1) != 0:
            return "Invalid Reading"
        elif status & (1 << 4) != 0:
            return "T-UNDER"
        elif status & (1 << 5) != 0:
            return "T-OVER"
        elif status & (1 << 6) != 0:
            return "S-UNDER"
        elif status & (1 << 7) != 0:
            return "S-OVER"
        else:
            raise InstrIOError("TC331: failed to get input temperature")

    def set_loop_PID(self, loop, auto, p, i, d):
        """Sets a loop's PID values or sets auto PID"""

        if auto:
            self.write(f"CMODE {loop},4")
            print("PID set auto")
        else:
            self.write(f"CMODE {loop},1")
            self.write(f"PID {loop},{p},{i},{d}")
            print("PID set manual")

    def set_loop_mout(self, loop, val):
        """Sets the loop manual heater output"""

        self.write(f"MOUT {loop},{val}")
        print(f"setting manual heater output to {val} for loop {loop}")

    def set_loop_setpoint(self, loop, val):
        """Sets the loop setpoint"""

        self.write(f"SETP {loop},{val}")
        print(f"setting the setpoint to {val} for loop {loop}")

    def set_input_settings(self, input, sensor_type, compensation):
        """Configures a loop's input settings:
        diode type, compensation"""

        self.write(f"INTYPE {input}, {sensor_type},{compensation}")
        print("setting input settings")

    def set_input_curve(self, input, curve):
        """Sets an input diode curve"""

        self.write(f"INCRV {input},{curve}")
        print("setting input diode curve")
