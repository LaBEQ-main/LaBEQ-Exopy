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

class ZM2376_SetFrequencyTask(InstrumentTask):


    # Time to wait before execution
    wait_time = Float().tag(pref=True)
    
    # frequency set point
    freq = Str().tag(pref=True)

    wait = set_default({'activated': True, 'wait': ['instr']})
    database_entries = set_default({'val': 0.0})

    def perform(self):
        
        sleep(self.wait_time)
        freq_setpoint = self.format_and_eval_string(self.freq)

        self.driver.set_frequency(freq_setpoint)
        self.write_in_database('val', freq_setpoint)

class ZM2376_MeasureTask(InstrumentTask):

    # Time to wait before execution
    wait_time = Float().tag(pref=True)
    
    # pri and sec parameter options
    pri = Enum('Z','Y','R','RP','RS','G','C','CP','CS','L','LP','LS','REAL','MLIN').tag(pref=True)
    sec = Enum('Q','D','PHAS','X','B','RS','RP','G','LP','RDC','IMAG','REAL').tag(pref=True)

    wait = set_default({'activated': True, 'wait': ['instr']})
    database_entries = set_default({'pri': 0.0, 'sec': 0.0})

    def perform(self):
        
        sleep(self.wait_time)

        params = [self.pri, self.sec]

        pri_val, sec_val = self.driver.fetch_measurements(params)

        self.write_in_database('pri', pri_val)
        self.write_in_database('sec', sec_val)