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

from exopy.tasks.api import InstrumentTask, InterfaceableTaskMixin

class NFLockInMeasureTask(InstrumentTask):
    """ Measure lock in output"""

    # Time to wait before execution
    wait_time = Float().tag(pref=True)

    val = Enum('R', 'Phase', 'X', 'Y').tag(pref=True)
    wait = set_default({'activated': True, 'wait': ['instr']})
    database_entries = set_default({'val': 0.0})

    def perform(self):
        
        sleep(self.wait_time)

        num = self.driver.measure(self.val)
        self.write_in_database('val', num)