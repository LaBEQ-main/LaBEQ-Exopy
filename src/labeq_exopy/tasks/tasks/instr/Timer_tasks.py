# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Authors - Frank Duffy, LaBEQ / Sardashti Research Group, Clemson University
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------

from time import sleep
from atom.api import Float, Str, Enum, set_default
from exopy.tasks.api import InstrumentTask, InterfaceableTaskMixin, TaskInterface

class InitiateTimer(InstrumentTask):
    """
        Set current time as start time.

    """
    # Time to wait before the ramp.
    wait_time = Float().tag(pref=True)

    database_entries = set_default({'start_time': 0.0})

    wait = set_default({'activated': True, 'wait': ['instr']})

    def perform(self):

        sleep(self.wait_time)
        start_time = self.driver.initiate_timer()
        self.write_in_database('start_time', start_time)

class GetElapsedTime(InstrumentTask):
    """
        Get elapsed time.

    """
    # Time to wait before the ramp.
    wait_time = Float().tag(pref=True)

    database_entries = set_default({'elapsed_time': 0.0})

    wait = set_default({'activated': True, 'wait': ['instr']})

    def perform(self):
        
        sleep(self.wait_time)
        elapsed_time = self.driver.get_elapsed_time()
        self.write_in_database('elapsed_time', elapsed_time)