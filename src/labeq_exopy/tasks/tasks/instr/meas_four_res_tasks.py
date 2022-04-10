# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyHqcLegacy Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Task to measure four wire resistance.

"""
from time import sleep

from atom.api import Float, set_default, Str

from exopy.tasks.api import (InterfaceableTaskMixin, InstrumentTask, TaskInterface)


class MeasFourResistanceTask(InterfaceableTaskMixin, InstrumentTask):
    """Measure a four wire resistance.

    Wait for any parallel operation before execution and then wait the
    specified time before perfoming the measure.

    """
    # Time to wait before the measurement.
    wait_time = Float().tag(pref=True)

    database_entries = set_default({'four_resistance': 1.0})

    wait = set_default({'activated': True, 'wait': ['instr']})

    def i_perform(self):
        """Wait and read the resistance.

        """
        sleep(self.wait_time)

        value = self.driver.read_four_resistance()
        self.write_in_database('four_resistance', value)

class Keithley2400MeasFourResistanceInterface(TaskInterface):
    """Measure a four wire resistance with Keithley 2400

    Wait for any parallel operation before execution and then wait the
    specified time before perfoming the measure.

    """

    source_mode = Str().tag(pref=True)
    source_type = Str().tag(pref=True)
    curr_comp = Float().tag(pref=True)
    volt_comp = Float().tag(pref=True)

    database_entries = set_default({'four_resistance': 1.0})

    def perform(self):
        """Wait and read the two wire resistance.

        """
        
        arg_list = [self.source_mode, self.source_type, self.curr_comp, self.volt_comp]
        value = self.task.driver.read_four_resistance(arg_list)
        self.task.write_in_database('four_resistance', value)
