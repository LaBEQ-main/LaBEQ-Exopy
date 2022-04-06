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

from atom.api import Float, set_default

from exopy.tasks.api import InstrumentTask


class MeasFourResistanceTask(InstrumentTask):
    """Measure a four wire resistance.

    Wait for any parallel operation before execution and then wait the
    specified time before perfoming the measure.

    """
    # Time to wait before the measurement.
    wait_time = Float().tag(pref=True)

    database_entries = set_default({'four_resistance': 1.0})

    wait = set_default({'activated': True, 'wait': ['instr']})

    def perform(self):
        """Wait and read the resistance.

        """
        sleep(self.wait_time)

        value = self.driver.read_four_resistance()
        self.write_in_database('four_resistance', value)