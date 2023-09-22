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
        super(LakeshoreTC331, self).open_connection(**para)
        self.write_termination = "\0"
        self.read_termination = "\r\n"

    def set_heater_range(self, range):
        """Sets the heater range"""

        self.write(f"RANGE {range}")

        if self.query("RANGE?") == f"{range}":
            print(f"heater range set to {range}")
        else:
            raise InstrIOError("TC331: failed to set heater range")

    def set_loop_control_parameters(
        self, loop, input, units, powerup_enable, heater_output_display
    ):
        """Configures a control loop's parameters:
        control input channel, setpoint units, on/off on startup, heater output display
        """

        self.write(
            f"CSET {loop},{input},{units},{powerup_enable},{heater_output_display}"
        )

        if (
            self.query("CSET?")
            == f"{input},{units},{powerup_enable},{heater_output_display}"
        ):
            print(f"set the control settings")
        else:
            raise InstrIOError("TC331: failed to set the control settings")

    def get_input_temperature(self, input):
        """Gets the temperature of an input in Kelvin"""

        status = int(self.query(f"RDGST? {input}"))

        if status == 0:
            return float(self.query(f"KRDG? {input}"))
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

            if self.query(f"CMODE? {loop}") == "4":
                print("PID set auto")
            else:
                raise InstrIOError("TC331: failed to set auto PID")

        else:
            self.write(f"CMODE {loop},1")

            if self.query(f"CMODE? {loop}") == "1":
                print("PID set manual")
            else:
                raise InstrIOError("TC331: failed to manual PID")

            self.write(f"PID {loop},{p},{i},{d}")

            if self.query(f"PID? {loop}") == f"{p},{i},{d}":
                print("PID values set")
            else:
                raise InstrIOError("TC331: failed to set PID values")

    def set_loop_mout(self, loop, val):
        """Sets the loop manual heater output"""

        self.write(f"MOUT {loop},{val}")

        if self.query(f"MOUT? {loop}") == f"{val}":
            print(f"set manual heater output to {val} for loop {loop}")
        else:
            raise InstrIOError("TC331: failed to set manual heater output")

    def set_loop_setpoint(self, loop, val):
        """Sets the loop setpoint"""

        self.write(f"SETP {loop},{val}")

        if self.query(f"SETP? {loop}") == f"{val}":
            print(f"set the setpoint to {val} for loop {loop}")
        else:
            raise InstrIOError("TC331: failed to set setpoint")

    def set_input_settings(self, input, sensor_type, compensation):
        """Configures a loop's input settings:
        diode type, compensation"""

        self.write(f"INTYPE {input},{sensor_type},{compensation}")
        print("setting input settings")

        if self.query(f"INTYPE? {input}") == f"{sensor_type},{compensation}":
            print(f"set input settings")
        else:
            raise InstrIOError("TC331: failed to set input settings")

    def set_input_curve(self, input, curve):
        """Sets an input diode curve"""

        self.write(f"INCRV {input},{curve}")
        print("setting input diode curve")

        if self.query(f"INCRV? {input}") == f"{curve}":
            print(f"set input diode curve")
        else:
            raise InstrIOError("TC331: failed to set input diode curve")
