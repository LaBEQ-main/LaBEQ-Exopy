#Jake Macdonald 7/8/22
"""Keithley6500 tasks

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
