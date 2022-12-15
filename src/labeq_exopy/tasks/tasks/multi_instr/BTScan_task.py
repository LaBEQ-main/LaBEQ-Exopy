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
from exopy.tasks.api import InstrumentTask, SimpleTask
from labeq_exopy.instruments.drivers.visa.Timer_driver import Timer

class BTScanTask(SimpleTask):
    """
        Set current time as start time.

    """
    # Time to wait before the ramp.
    wait_time = Float().tag(pref=True)

    database_entries = set_default({'start_time': 0.0})

    wait = set_default({'activated': True})

    def perform(self):

        connection_info = {"resource_name" : "Timer"}
        timer = Timer(connection_info)

        time = timer.initiate_timer()

        print("HELLO WORLD")
        self.write_in_database('start_time', time)

        