# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Authors - Matthew Everette, LaBEQ / Sardashti Research Group, Clemson University
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------

"""Tasks to control the Keysight EDUX1052G Oscilloscope"""

from atom.api import Enum, Float, set_default, Bool, Str, Int

from exopy.tasks.api import InstrumentTask


class KeysightEDUX1052GConfigureTask(InstrumentTask):
    ChannelNum = Enum("1", "2").tag(pref=True)
    UseAutoscale = Bool().tag(pref=True)
    TriggerLevel = Float().tag(pref=True)
    TriggerSlope = Enum("negative", "positive", "either", "alternate").tag(pref=True)
    AcquisitionType = Enum("normal", "average", "high resolution", "peak").tag(
        pref=True
    )
    AvgCount = Int().tag(pref=True)

    def perform(self):
        self.driver.configure(
            self.ChannelNum,
            self.UseAutoscale,
            self.TriggerLevel,
            self.TriggerSlope,
            self.AcquisitionType,
            self.AvgCount,
        )


class KeysightEDUX1052GCaptureTask(InstrumentTask):
    ChannelNum = Enum("1", "2").tag(pref=True)

    def perform(self):
        self.driver.capture(self.ChannelNum)


class KeysightEDUX1052GMeasureTask(InstrumentTask):
    ChannelNum = Enum("1", "2").tag(pref=True)

    database_entries = set_default({"amplitude": 0, "frequency": 0})

    def perform(self):
        amplitude = self.driver.measure_amplitude(self.ChannelNum)
        self.write_in_database("amplitude", amplitude)

        frequency = self.driver.measure_frequency(self.ChannelNum)
        self.write_in_database("frequency", frequency)


class KeysightEDUX1052GGetImageTask(InstrumentTask):
    ChannelNum = Enum("1", "2").tag(pref=True)
    File = Str().tag(pref=True)

    def perform(self):
        data = self.driver.get_screen_image(self.ChannelNum)
        with open(self.File, "wb") as f:
            f.write(data)
