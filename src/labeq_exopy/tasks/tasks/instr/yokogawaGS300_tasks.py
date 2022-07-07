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


class SetRange(InstrumentTask):
    """Ask a lock-in to perform a measure.

    Wait for any parallel operationbefore execution.

    """
    #: Value to retrieve.
    MeasMode = Enum('MIN', '1E-3', '10E-3', '100E-3', '200E-3', 'MAX','Freq','Phase').tag(pref=True)
    
    #: Time to wait before performing the measurement.
    waiting_time = Float().tag(pref=True)

    database_entries = set_default({'range_v': 1.0})

    wait = set_default({'activated': True, 'wait': ['instr']})

    def perform(self):
        """Wait and query the last value in the instrument buffer.

        """
        range_val = Float().tag(pref=True)

        #measurement selection
        if self.MeasMode == 'MIN':
            value = self.driver.read_x()
            self.write_in_database('x', value)
        elif self.MeasMode == '1E-3':
            value = self.driver.read_y()
            self.write_in_database('y', value)
        elif self.MeasMode == '10E-3':
            value_x, value_y = self.driver.read_xy()
            self.write_in_database('x', value_x)
            self.write_in_database('y', value_y)
        elif self.MeasMode == '100E-3':
            value = self.driver.read_amplitude()
            self.write_in_database('amplitude', value)
        elif self.MeasMode == '200E-3':
            value = self.driver.read_theta()
            self.write_in_database('theta', value)
        elif self.MeasMode == 'MAX':
            amplitude, theta = self.driver.read_amp_and_theta()
            self.write_in_database('amplitude', amplitude)
            self.write_in_database('theta', theta)
       
        value = self.driver.set_range(self.range_val)
        self.write_in_database('range_val', value)