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

import os


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
    CaptureChannel1 = Bool().tag(pref=True)
    CaptureChannel2 = Bool().tag(pref=True)

    def perform(self):
        channel_nums = []
        if self.CaptureChannel1:
            channel_nums.append(1)
        if self.CaptureChannel2:
            channel_nums.append(2)

        self.driver.capture(channel_nums)


class KeysightEDUX1052GMeasureTask(InstrumentTask):
    ChannelNum = Enum("1", "2").tag(pref=True)
    MeasureAmplitude = Bool().tag(pref=True)
    MeasureFrequency = Bool().tag(pref=True)
    MeasurePeriod = Bool().tag(pref=True)
    MeasureAverage = Bool().tag(pref=True)
    MeasureMax = Bool().tag(pref=True)
    MeasureMin = Bool().tag(pref=True)
    MeasureRMS = Bool().tag(pref=True)

    database_entries = set_default(
        {
            "amplitude": None,
            "frequency": None,
            "period": None,
            "average": None,
            "max": None,
            "min": None,
            "rms": None,
        }
    )

    def perform(self):
        self.driver.set_measure_source(self.ChannelNum)

        if self.MeasureAmplitude:
            amplitude = self.driver.measure_amplitude()
            self.write_in_database("amplitude", amplitude)

        if self.MeasureFrequency:
            frequency = self.driver.measure_frequency()
            self.write_in_database("frequency", frequency)

        if self.MeasurePeriod:
            period = self.driver.measure_period()
            self.write_in_database("period", period)

        if self.MeasureAverage:
            average = self.driver.measure_average()
            self.write_in_database("average", average)

        if self.MeasureMax:
            max = self.driver.measure_max()
            self.write_in_database("max", max)

        if self.MeasureMin:
            min = self.driver.measure_min()
            self.write_in_database("min", min)

        if self.MeasureRMS:
            rms = self.driver.measure_rms()
            self.write_in_database("rms", rms)


class KeysightEDUX1052GGetImageTask(InstrumentTask):
    #: Folder in which to save the data.
    folder = Str("{default_path}").tag(pref=True)

    #: Name of the file in which to write the data.
    filename = Str().tag(pref=True)

    def perform(self):
        full_folder_path = self.format_string(self.folder)
        filename = self.format_string(self.filename)
        full_path = os.path.join(full_folder_path, filename)

        data = self.driver.get_screen_image()

        with open(full_path, "wb") as f:
            f.write(data)


class KeysightEDUX1052GGetWaveformTask(InstrumentTask):
    ChannelNum = Enum("1", "2").tag(pref=True)
    File = Str().tag(pref=True)

    def perform(self):
        preamble, data = self.driver.get_waveform(self.ChannelNum)
        with open(self.File, "w") as f:
            f.write(preamble)
            f.write(data)
