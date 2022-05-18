# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyHqcLegacy Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Task to measure DC current.

"""
from re import X
from time import sleep

from atom.api import Float, Str, set_default

from exopy.tasks.api import InstrumentTask


class PlotTask(InstrumentTask):
    """Plot

    Wait for any parallel operation before execution and then wait the
    specified time.

    """
    # Time to wait before the measurement.
    wait_time = Float().tag(pref=True)
    x = Str().tag(pref=True)
    y = Str().tag(pref=True)

    database_entries = set_default({'plot': 1.0})

    wait = set_default({'activated': True, 'wait': ['instr']})

    def perform(self):
        """Wait and read the AC current.

        """
        # sleep(self.wait_time)

        x = self.format_and_eval_string(self.x)
        y = self.format_and_eval_string(self.y)
        self.driver.test(x, y)
        # self.write_in_database('plot', value)
