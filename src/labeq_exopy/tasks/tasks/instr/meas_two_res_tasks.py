# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyHqcLegacy Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Task to measure two wire resistance.

"""
from statistics import mode
from time import sleep

from atom.api import Float, set_default, Str, Enum

from exopy.tasks.api import (InterfaceableTaskMixin, InstrumentTask, TaskInterface)


class MeasTwoResistanceTask(InterfaceableTaskMixin, InstrumentTask):
    """Measure a two wire resistance.

    Wait for any parallel operation before execution and then wait the
    specified time before perfoming the measure.

    """
    # Time to wait before the measurement.
    wait_time = Float().tag(pref=True)

    database_entries = set_default({'two_resistance': 1.0})

    wait = set_default({'activated': True, 'wait': ['instr']})

    def i_perform(self):
        """Wait and read the two wire resistance.

        """
        sleep(self.wait_time)

        value = self.driver.read_two_resistance()
        self.write_in_database('two_resistance', value)

class Keithley2400MeasTwoResistanceInterface(TaskInterface):
    """Measure a two wire resistance.

    Wait for any parallel operation before execution and then wait the
    specified time before perfoming the measure.

    """

    source_mode = Enum('Manual', 'Auto').tag(pref=True)
    source_type = Str().tag(pref=True)
    curr_comp = Float().tag(pref=True)
    volt_comp = Float().tag(pref=True)

    database_entries = set_default({'two_resistance': 1.0})

    def perform(self):
        """Wait and read the two wire resistance.

        """
        
        arg_list = [self.source_mode, self.source_type, self.curr_comp, self.volt_comp]
        value = self.task.driver.read_two_resistance(arg_list)
        self.task.write_in_database('two_resistance', value)

