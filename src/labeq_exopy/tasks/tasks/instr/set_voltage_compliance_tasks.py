# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyHqcLegacy Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Task to set voltage compliance.

"""
from time import sleep

from atom.api import Float, set_default

from exopy.tasks.api import InstrumentTask


class SetVoltageComplianceTask(InstrumentTask):
    """set voltage compliance.

    Wait for any parallel operation before execution and then wait the
    specified time before perfoming the measure.

    """
    comp_v = Float().tag(pref=True)

    database_entries = set_default({'comp_v': 0.0})

    def perform(self):
        """Set comp_v.

        """

        value = self.comp_v
        self.driver.set_voltage_comp(value)
        self.write_in_database('comp_v', value)
