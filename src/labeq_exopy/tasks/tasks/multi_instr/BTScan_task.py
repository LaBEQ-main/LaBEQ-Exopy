# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Authors - Frank Duffy, LaBEQ / Sardashti Research Group, Clemson University
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
import numpy as np

from time import sleep
from atom.api import Float, Str, Enum, set_default
from exopy.tasks.api import InstrumentTask, SimpleTask
from labeq_exopy.instruments.drivers.visa.Timer_driver import Timer
from labeq_exopy.instruments.drivers.visa.Oxford_MercuryiTC_driver import MercuryiTC
from labeq_exopy.instruments.drivers.visa.oxford_mercuryips import MercuryiPS 
from labeq_exopy.instruments.drivers.visa.NF_LI5650_driver import LI5650
from labeq_exopy.instruments.drivers.visa.lock_in_sr830 import LockInSR830

class BTScanTask(SimpleTask):
    """
        Set current time as start time.

    """
    wait_time       = Float().tag(pref=True)
    directory       = Str().tag(pref=True)
    file            = Str().tag(pref=True)
    field_max       = Float().tag(pref=True)
    field_min       = Float().tag(pref=True)
    field_rate      = Float().tag(pref=True)
    temp_max        = Float().tag(pref=True)
    temp_min        = Float().tag(pref=True)
    temp_step       = Float().tag(pref=True)
    
    database_entries = set_default({'start_time': 0.0})
    wait = set_default({'activated': True})

    def perform(self):
        
        # create device objects
        timer   = Timer({"resource_name" : "Timer"})
        itc     = MercuryiTC({"resource_name" : "MercuryITC"})
        ips     = MercuryiPS({"resource_name" : "MercuryIPS"})
        nf      = LI5650({"resource_name" : "NF LI5650"})
        pg1     = LockInSR830({"resource_name" : "PG1"})
        srs1    = LockInSR830({"resource_name" : "SRS1"})

        # calculate number of temp steps
        Tnum = np.absolute(self.Tmax - self.Tmin)/self.Tstep

        # get start time in linux format and save to db
        time = timer.initiate_timer()
        self.write_in_database('start_time', time)

        # check that the probe temp is not currently higher than tmin
        # check that field is not currently higher than the field_min
        # if checks fail, notify user and initialize system into start stat with field_min and temp_min


        # for i in range(Tnum):
            # set probe temp through itc
            # set target field as either field_max or field_min based on evenness of i
            # if (num % 2) == 0 set target field as field_max
            # else set target field as field_min
            # monitor for steady-state using pandas.rolling to compute moving average
            # start magnet sweep to min after reaching steady-state temp
            # while current field is less than target field, measure amplitude, phase, probe temp, vti temp, vti pressure, vti valve
                # make requisite measurements and then save to the designated file
                # a
        
        
        
        

        