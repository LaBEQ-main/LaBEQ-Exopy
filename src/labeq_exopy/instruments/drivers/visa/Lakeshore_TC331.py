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
            print(f"set heater range")
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
        self.wait_to_complete()

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
            self.wait_to_complete()

            if self.query(f"CMODE? {loop}") == "4":
                print("set PID auto")
            else:
                raise InstrIOError("TC331: failed to set auto PID")

        else:
            self.write(f"CMODE {loop},1")
            self.wait_to_complete()

            if self.query(f"CMODE? {loop}") == "1":
                print("set PID manual")
            else:
                raise InstrIOError("TC331: failed to manual PID")

            self.write(f"PID {loop},{p},{i},{d}")
            self.wait_to_complete()

            if [float(x) for x in self.query(f"PID? {loop}").split(",")] == [p, i, d]:
                print("set PID values")
            else:
                raise InstrIOError("TC331: failed to set PID values")

    def set_loop_mout(self, loop, val):
        """Sets the loop manual heater output"""

        self.write(f"MOUT {loop},{val}")
        self.wait_to_complete()

        if float(self.query(f"MOUT? {loop}")) == val:
            print(f"set manual heater output")
        else:
            raise InstrIOError("TC331: failed to set manual heater output")

    def set_setpoint(self, val):
        """Sets the setpoint"""

        self.write(f"SETP {val}")
        self.wait_to_complete()

        if float(self.query(f"SETP?")) == val:
            print(f"set the setpoint")
        else:
            raise InstrIOError("TC331: failed to set setpoint")

    def set_input_type(self, input, sensor_type, compensation):
        """Configures a loop's input type:
        diode type, compensation"""

        # compensation is always 0 if the input type is a diode
        if sensor_type in [0, 1]:
            compensation = 0

        self.write(f"INTYPE {input},{sensor_type},{compensation}")
        # self.wait_to_complete() for some reason this breaks the INTYPE command

        if self.query(f"INTYPE? {input}") == f"{sensor_type},{compensation}":
            print(f"set input settings")
        else:
            raise InstrIOError("TC331: failed to set input settings")

    def set_input_curve(self, input, curve):
        """Sets an input diode curve"""

        self.write(f"INCRV {input},{curve}")
        self.wait_to_complete()

        if self.query(f"INCRV? {input}") == f"{curve:02}":
            print(f"set input diode curve")
        else:
            raise InstrIOError("TC331: failed to set input diode curve")

    def wait_to_complete(self):
        return self.query("*OPC?")
