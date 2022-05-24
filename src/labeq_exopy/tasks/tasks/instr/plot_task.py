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
    xcol = Str().tag(pref=True)
    ycol = Str().tag(pref=True)
    file = Str().tag(pref=True)

    wait = set_default({'activated': True, 'wait': ['instr']})

    def perform(self):
        """
        """

        self.driver.xcol = self.xcol
        self.driver.ycol = self.ycol
        self.driver.file = self.file
        self.driver.start()
