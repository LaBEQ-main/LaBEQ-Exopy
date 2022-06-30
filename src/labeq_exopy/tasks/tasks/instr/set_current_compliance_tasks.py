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


class SetCurrentComplianceTask(InstrumentTask):
    """set current compliance.

    Wait for any parallel operation before execution and then wait the
    specified time before perfoming the measure.

    """
    comp_c = Float().tag(pref=True)

    database_entries = set_default({'comp_c': 1.0})

    def perform(self):
        """Set comp_c.

        """
        value = self.comp_c
        self.driver.set_current_comp(value)
        self.write_in_database('comp_c', value)
