# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Authors - Matthew Everette, LaBEQ / Sardashti Research Group, Clemson University
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------

"""Driver for Keysight EDUX1052G Oscilloscope"""

from ..driver_tools import InstrIOError
from ..visa_tools import VisaInstrument


class KeysightEDUX1052G(VisaInstrument):
    def open_connection(self, **para):
        super(KeysightEDUX1052G, self).open_connection(**para)
        self.write_termination = "\r\n"
        self.read_termination = "\n"

        # Clear status and load default setup
        self.write("*CLS")
        self.write("*RST")

    def configure(
        self,
        channel_num,
        use_autoscale,
        trigger_level,
        trigger_slope,
        acquisition_type,
        avg_count=None,
    ):
        if use_autoscale:
            self.write(":AUToscale")

        self.write(":TRIGger:MODE EDGE")
        assert self.query(":TRIGger:MODE?") == "EDGE"

        self.write(f":TRIGger:EDGE:SOURce CHANnel{channel_num}")
        assert self.query(":TRIGger:EDGE:SOURce?") == f"CHAN{channel_num}"

        self.write(f":TRIGger:EDGE:LEVel {trigger_level}")
        assert float(self.query(":TRIGger:EDGE:LEVel?")) == trigger_level

        if trigger_slope == "negative":
            trigger_slope = "NEG"
        elif trigger_slope == "positive":
            trigger_slope = "POS"
        elif trigger_slope == "either":
            trigger_slope = "EITH"
        elif trigger_slope == "alternate":
            trigger_slope = "ALT"
        else:
            raise InstrIOError("EDUX1025G: invalid value for 'trigger_slope'")

        self.write(f":TRIGger:EDGE:SLOPe {trigger_slope}")
        assert self.query(":TRIGger:EDGE:SLOPe?") == trigger_slope

        if acquisition_type == "normal":
            self.write(":ACQuire:TYPE NORMal")
            assert self.query(":ACQuire:TYPE?") == "NORM"
        elif acquisition_type == "average":
            if avg_count:
                self.write(":ACQuire:TYPE AVERage")
                assert self.query(":ACQuire:TYPE?") == "AVER"

                self.write(f":ACQuire:COUNt {avg_count}")
                assert int(self.query(":ACQuire:COUNt?")) == avg_count
            else:
                raise InstrIOError(
                    "EDUX1025G: Must specify avg_count for acquisition_type 'average'"
                )
        elif acquisition_type == "high resolution":
            self.write(":ACQuire:TYPE HRESolution")
            assert self.query(":ACQuire:TYPE?") == "HRES"
        elif acquisition_type == "peak":
            self.write(":ACQuire:TYPE PEAK")
            assert self.query(":ACQuire:TYPE?") == "PEAK"
        else:
            raise InstrIOError(
                f"EDUX1025G: Invalid acquisition_type '{acquisition_type}'"
            )

    def capture(self, channel_nums):
        self.write(
            f":DIGitize CHANnel{', '.join([f'CHANnel{num}' for num in channel_nums])}"
        )

    def set_measure_source(self, channel_num):
        self.write(f":MEASure:SOURce CHANnel{channel_num}")
        assert self.query(":MEASure:SOURce?") == f"CHAN{channel_num}"

    def measure_amplitude(self):
        self.write(":MEASure:VAMPlitude")
        return float(self.query(":MEASure:VAMPlitude?"))

    def measure_frequency(self):
        self.write(":MEASure:FREQuency")
        return float(self.query(":MEASure:FREQuency?"))

    def measure_period(self):
        self.write(":MEASure:PERiod")
        return float(self.query(":MEASure:PERiod?"))

    def measure_average(self):
        self.write(":MEASure:VAVerage")
        return float(self.query(":MEASure:VAVerage?"))

    def measure_max(self):
        self.write(":MEASure:VMAX")
        return float(self.query(":MEASure:VMAX?"))

    def measure_min(self):
        self.write(":MEASure:VMIN")
        return float(self.query(":MEASure:VMIN?"))

    def measure_rms(self):
        self.write(":MEASure:VRMS")
        return float(self.query(":MEASure:VRMS?"))

    def get_screen_image(self, channel_num):
        self.write(f":MEASure:SOURce CHANnel{channel_num}")
        assert self.query(":MEASure:SOURce?") == f"CHAN{channel_num}"

        self.write(":HARDcopy:INKSaver OFF")
        assert self.query(":HARDcopy:INKSaver?") == "OFF"

        return self.query(":DISPlay:DATA? PNG, COLor")

    def get_waveform(self, channel_num):
        self.write(":WAVeform:POINts:MODE NORMal")
        assert self.query(":WAVeform:POINts:MODE?") == f"NORMal"

        self.write(f":WAVeform:SOURce CHANnel{channel_num}")
        assert self.query(":WAVeform:SOURce?") == f"CHAN{channel_num}"

        self.write(":WAVeform:FORMat BYTE")
        assert self.query(":WAVeform:FORMat?") == "BYTE"

        preamble = self.query(":WAVeform:PREamble?")

        data = self.query(":WAVEFORM:DATA?")

        return preamble, data
