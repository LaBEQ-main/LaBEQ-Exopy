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
    MeasMode = Enum('X', 'Y', 'X&Y', 'Amp', 'Theta', 'Amp&Theta','Freq','Phase').tag(pref=True)
    
    #: Time to wait before performing the measurement.
    waiting_time = Float().tag(pref=True)

    database_entries = set_default({'x': 1.0,'y':1.0, 'amplitude':1.0, 'theta':1.0,'frequency':1.0,'phase':1.0})

    wait = set_default({'activated': True, 'wait': ['instr']})

    def perform(self):
        """Wait and query the last value in the instrument buffer.

        """
        sleep(self.waiting_time)
        #measurement selection
        if self.MeasMode == 'X':
            value = self.driver.read_x()
            self.write_in_database('x', value)
        elif self.MeasMode == 'Y':
            value = self.driver.read_y()
            self.write_in_database('y', value)
        elif self.MeasMode == 'X&Y':
            value_x, value_y = self.driver.read_xy()
            self.write_in_database('x', value_x)
            self.write_in_database('y', value_y)
        elif self.MeasMode == 'Amp':
            value = self.driver.read_amplitude()
            self.write_in_database('amplitude', value)
        elif self.MeasMode == 'Theta':
            value = self.driver.read_theta()
            self.write_in_database('theta', value)
        elif self.MeasMode == 'Amp&Theta':
            amplitude, theta = self.driver.read_amp_and_theta()
            self.write_in_database('amplitude', amplitude)
            self.write_in_database('theta', theta)
        elif self.MeasMode == 'Freq':
            value = self.driver.read_frequency()
            self.write_in_database('frequency', value)
        elif self.MeasMode == 'Phase':
            value = self.driver.read_phase()
            self.write_in_database('phase', value)

    def _post_setattr_MeasMode(self, old, new):
        """ Update the database entries acording to the MeasMode.

        """
        entries = self.database_entries.copy()
        for k in ('x', 'y', 'amplitude', 'theta','frequency','phase'):
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
        elif new == 'Theta':
            entries['theta'] = 1.0
        elif new == 'Amp&Theta':
            entries['amplitude'] = 1.0
            entries['theta'] = 1.0
        elif new == 'Freq':
            entries['frequency'] = 1.0
        elif new == 'Phase':
            entries['phase'] = 1.0

        self.database_entries = entries
        