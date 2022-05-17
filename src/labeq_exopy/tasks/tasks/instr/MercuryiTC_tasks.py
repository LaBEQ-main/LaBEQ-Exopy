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

class ReadTempSensorTask(TaskInterface):
    """ Reads the specified device value for iTC"""

    # Time to wait before the reading.
    wait_time = Float().tag(pref=True)
    temp_sensor = Enum('1', '2', '3').tag(pref=True)

    # temp_sensor = Enum('Magnet_MB1.T1', 'PT1_DB8.T1', 'PT2_DB7.T1').tag(pref=True)
    # value = Enum('VOLT', 'CURR', 'POWR', 'RES', 'TEMP', 'SLOP').tag(pref=True)

    # wait_time = set_default({'activated': True, 'wait': ['instr']})

    # database_entries = set_default({'val': 0.0})

    def perform(self):
        """Wait and read the chosen value from the specified temperature sensor.

        """
        sleep(self.wait_time)
        # val = self.driver.read_sensor(self.temp_sensor, self.value)
        # self.write_in_database('val', val)