# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyHqcLegacy Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Task to source dc current.

"""
from time import sleep

from atom.api import Float, set_default, Str

from exopy.tasks.api import InstrumentTask


class SourceDCCurrentTask(InstrumentTask):
    """source a dc current.

    Wait for any parallel operation before execution and then wait the
    specified time before perfoming the measure.

    """
    # Time to wait before the measurement.
    wait_time = Float().tag(pref=True)
    source_c = Str().tag(pref=True)

    database_entries = set_default({'source_current_dc': 1.0})

    wait = set_default({'activated': True, 'wait': ['instr']})


    def perform(self):
        """Wait and source the DC current.

        """
        sleep(self.wait_time)
        
        #returns float if given a float, returns database entry value type if given a database entry name
        value = self.format_and_eval_string(self.source_c)

        self.driver.source_current_dc(value)
        self.write_in_database('source_current_dc', value)
