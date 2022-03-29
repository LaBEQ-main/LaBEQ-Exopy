# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyHqcLegacy Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Task to perform a lock-in measurement.

"""
from time import sleep

from atom.api import (Enum, Float, set_default)

from exopy.tasks.api import InstrumentTask


class LockInMeasureTask(InstrumentTask):
    """Ask a lock-in to perform a measure.

    Wait for any parallel operationbefore execution.

    """
    #: Value to retrieve.
    mode = Enum('X', 'Y', 'X&Y', 'Amp', 'Phase', 'Amp&Phase').tag(pref=True)

    #: Time to wait before performing the measurement.
    waiting_time = Float().tag(pref=True)

    database_entries = set_default({'x': 1.0})

    wait = set_default({'activated': True, 'wait': ['instr']})

    def perform(self):
        """Wait and query the last value in the instrument buffer.

        """
        sleep(self.waiting_time)

        if self.mode == 'X':
            value = self.driver.read_x()
            self.write_in_database('x', value)
        elif self.mode == 'Y':
            value = self.driver.read_y()
            self.write_in_database('y', value)
        elif self.mode == 'X&Y':
            value_x, value_y = self.driver.read_xy()
            self.write_in_database('x', value_x)
            self.write_in_database('y', value_y)
        elif self.mode == 'Amp':
            value = self.driver.read_amplitude()
            self.write_in_database('amplitude', value)
        elif self.mode == 'Phase':
            value = self.driver.read_phase()
            self.write_in_database('phase', value)
        elif self.mode == 'Amp&Phase':
            amplitude, phase = self.driver.read_amp_and_phase()
            self.write_in_database('amplitude', amplitude)
            self.write_in_database('phase', phase)

    def _post_setattr_mode(self, old, new):
        """ Update the database entries acording to the mode.

        """
        entries = self.database_entries.copy()
        for k in ('x', 'y', 'amplitude', 'phase'):
            if k in entries:
                del entries[k]
        if new == 'X':
            entries['x'] = 1.0
        elif new == 'Y':
            entries['y'] = 1.0
        elif new == 'X&Y':
            entries['x'] = 1.0
            entries['y'] = 1.0
        elif new == 'Amp':
            entries['amplitude'] = 1.0
        elif new == 'Phase':
            entries['phase'] = 1.0
        elif new == 'Amp&Phase':
            entries['amplitude'] = 1.0
            entries['phase'] = 1.0

        self.database_entries = entries
