# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyHqcLegacy Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Task to set current compliance.

"""
from time import sleep

from atom.api import Float, set_default

from exopy.tasks.api import InstrumentTask


class SetRange(InstrumentTask):
    """set current compliance.

    Wait for any parallel operation before execution and then wait the
    specified time before perfoming the measure.

    """
    range_val = Float().tag(pref=True)

    database_entries = set_default({'range_val': 1.0})

    def perform(self):
        value = self.driver.set_range(self.range_val)
        self.write_in_database('range_val', value)
