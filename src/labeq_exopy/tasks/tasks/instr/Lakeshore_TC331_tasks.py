# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Authors - Matthew Everette, LaBEQ / Sardashti Research Group, Clemson University
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------

"""Tasks to control the Lakeshore TC331"""

from cmath import sin
from this import d
from time import sleep

from atom.api import Enum, Float, set_default, Bool, Str

from exopy.tasks.api import InstrumentTask


class LakeshoreTC331MeasureTask(InstrumentTask):
    MeasInput = Enum("A", "B").tag(pref=True)
    DualTemp = Bool(False).tag(pref=True)

    database_entries = set_default({"A_Temp": 0, "B_Temp": 0})

    def perform(self):
        if self.MeasInput == "A":
            value = self.driver.get_input_temperature(self.MeasInput)
            self.write_in_database("A_Temp", value)
        elif self.MeasInput == "B":
            value = self.driver.get_input_temperature(self.MeasInput)
            self.write_in_database("B_Temp", value)

        if self.DualTemp:
            if self.MeasInput == "A":
                value2 = self.driver.get_input_temperature("B")
                self.write_in_database("B_Temp", value2)
            if self.MeasInput == "B":
                value2 = self.driver.get_input_temperature("A")
                self.write_in_database("A_Temp", value2)

    def _post_setattr_MeasInput(self, old, new):
        """Update the database entries according to the MeasInput"""
        entries = self.database_entries.copy()
        for k in ("A", "B"):
            if k in entries:
                del entries[k]
        if new == "A":
            entries["A_Temp"] = 0
        elif new == "B":
            entries["B_Temp"] = 0

        self.database_entries = entries


class LakeshoreTC340ConfigureTask(InstrumentTask):
    Loop = Enum("1", "2").tag(pref=True)
    CntrlChannel = Enum("A", "B").tag(pref=True)
    SetpUnits = Enum("K", "C", "Sensor").tag(pref=True)
    AutoPID = Bool(False).tag(pref=True)
    P = Float(50).tag(pref=True)
    I = Float(20).tag(pref=True)
    D = Float(13).tag(pref=True)
    Mout = Float().tag(pref=True)
    ConfigInput = Enum("A", "B").tag(pref=True)
    Sensor = Enum(
        "Silicon Diode",
        "GaAlAs Diode",
        "100\u03A9 Platinum/250",
        "100\u03A9 Platinum/500",
        "1000\u03A9 Platinum",
        "NTC RTD",
        "Thermocouple 25 mV",
        "Thermocouple 50 mV",
        "2.5 V, 1 mA",
        "7.5 V, 1 mA",
    ).tag(pref=True)
    InputCompensation = Enum("On", "Off").tag(pref=True)
    Curve = Enum(
        "No Curve", "DT-470", "DT-500-D", "DT-500-E1", "DT-670", "PT-100", "PT-1000"
    ).tag(pref=True)

    database_entries = set_default({"A": 1.0})

    def perform(self):
        """Wait and query the last value in the instrument buffer."""

        # Convert Sensor to integer
        if self.Sensor == "Silicon Diode":
            sensor = 0
        elif self.Sensor == "GaAlAs Diode":
            sensor = 1
        elif self.Sensor == "100\u03A9 Platinum/250":
            sensor = 2
        elif self.Sensor == "100\u03A9 Platinum/500":
            sensor = 3
        elif self.Sensor == "1000\u03A9 Platinum":
            sensor = 4
        elif self.Sensor == "NTC RTD":
            sensor = 5
        elif self.Sensor == "Thermocouple 25 mV":
            sensor = 6
        elif self.Sensor == "Thermocouple 50 mV":
            sensor = 7
        elif self.Sensor == "2.5 V, 1 mA":
            sensor = 8
        elif self.Sensor == "7.5 V, 1 mA":
            sensor = 9

        # Convert InputCompensation to integer
        if self.InputCompensation == "On":
            input_compensation = 1
        elif self.InputCompensation == "Off":
            input_compensation = 0

        # Set input settings
        self.driver.set_input_settings(self.ConfigInput, sensor, input_compensation)

        # Convert Curve to integer
        if self.Curve == "No Curve":
            curve = 0
        elif self.Curve == "DT-470":
            curve = 1
        elif self.Curve == "DT-670":
            curve = 2
        elif self.Curve == "DT-500-D":
            curve = 3
        elif self.Curve == "DT-500-E1":
            curve = 4
        elif self.Curve == "PT-100":
            curve = 6
        elif self.Curve == "PT-1000":
            curve = 7
        elif self.Curve == "RX-102A-AA":
            curve = 8
        elif self.Curve == "RX-202A-AA":
            curve = 9
        elif self.Curve == "Type K":
            curve = 12
        elif self.Curve == "Type E":
            curve = 13
        elif self.Curve == "Type T":
            curve = 14
        elif self.Curve == "AuFe 0.03%":
            curve = 15
        elif self.Curve == "AuFe 0.07%":
            curve = 16

        # Make sure the sensor and curve are compatible, and set the input curve
        if (
            (curve in [0])
            or (sensor in [0] and curve in [1, 2, 3, 4])
            or (sensor in [2, 3] and curve in [6])
            or (sensor in [4] and curve in [7])
            or (sensor in [5] and curve in [8, 9])
            or (sensor in [6, 7] and curve in [12, 13, 14, 15, 16])
        ):
            self.driver.set_input_curve(self.ConfigInput, curve)
        else:
            print("ERROR: Invalid curve. No curve set")
            self.driver.set_input_curve(self.ConfigInput, 0)

        # Convert SetpUnits to integer
        if self.SetpUnits == "K":
            setp_units = 1
        elif self.SetpUnits == "C":
            setp_units = 2
        elif self.SetpUnits == "Sensor":
            setp_units = 3

        # Set control parameters
        self.driver.set_control_parameters(
            self.Loop, self.CntrlChannel, setp_units, 1, 2
        )

        # Set auto/manual PID
        self.driver.set_PID(self.Loop, self.AutoPID, self.P, self.I, self.D)

        # Set manual heater output
        if not self.AutoPID:
            self.driver.set_mout(self.Loop, self.Mout)


class LakeshoreTC340HeaterSetpointAndRangeTask(InstrumentTask):
    Loop = Enum("1", "2").tag(pref=True)
    Setpoint = Str("300").tag(pref=True)
    SetHtrRange = Enum("HIGH", "MEDIUM", "LOW", "OFF").tag(pref=True)

    def perform(self):
        # Set the heater set point
        setpoint = self.format_and_eval_string(self.Setpoint)
        self.driver.set_setpoint(self.Loop, setpoint)

        # Set the heater range
        if self.SetHtrRange == "HIGH":
            htr_range = "3"
        elif self.SetHtrRange == "MEDIUM":
            htr_range = "2"
        elif self.SetHtrRange == "LOW":
            htr_range = "1"
        elif self.SetHtrRange == "OFF":
            htr_range = "0"
        self.driver.set_heater_range(htr_range)
