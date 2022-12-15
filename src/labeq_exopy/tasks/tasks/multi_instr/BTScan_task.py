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
    field_rate_max  = Float().tag(pref=True)
    field_rate_safe = Float().tag(pref=True)
    temp_max        = Float().tag(pref=True)
    temp_min        = Float().tag(pref=True)
    temp_step       = Float().tag(pref=True)
    
    database_entries = set_default({'start_time': 0.0})
    wait = set_default({'activated': True})

    def perform(self):
        
        # create device objects
        timer   = Timer({"resource_name" : "Timer"})
        # itc     = MercuryiTC({"resource_name" : "MercuryITC"})
        # ips     = MercuryiPS({"resource_name" : "MercuryIPS"})
        # nf      = LI5650({"resource_name" : "NF LI5650"})
        # pg1     = LockInSR830({"resource_name" : "PG1"})
        # srs1    = LockInSR830({"resource_name" : "SRS1"})

        # calculate number of temp steps
        Tnum = np.absolute(self.Tmax - self.Tmin)/self.Tstep

        # get start time in linux format and save to db
        starttime = timer.initiate_timer()
        self.write_in_database('start_time', starttime)

        # set up save file with headers

        # check that the probe temp is not currently higher than tmin
        # check that field is not currently higher than the field_min
        # if checks fail, notify user and initialize system into start stat with field_min and temp_min


        # for i in range(Tnum):
            # set probe temp through itc to temp_min + i*temp_step
            # wait for probe temp to reach steady-state and monitor in while loop
            # set target field as either field_max or field_min based on evenness of i
            # if (num % 2) == 0 set target field as field_min
            # else set target field as field_max
            # monitor for steady-state using pandas.rolling to compute moving average
            # start magnet sweep to min after reaching steady-state temp
            # get the current field
            # while absolute value of target field - current field > 0.01, 
                # measure current field, amplitude, phase, probe temp, vti temp, vti pressure, vti valve and time since start, time since epoch
                # save to the designated file
                # if absolute value of current field is less than 0.3 (safe zone) && current field rate == field_rate_max
                    # set current_field_rate to field_rate_safe
                # if absolute value of current field is greater than 0.3 (safe zone) && current field rate == field_rate_min
                    #set current_field_rate to field_rate_max

        # after all temp steps have been completed, return the magnet back to final field with defualt 0.
        # set target_field to 0
        # while abs(target_field - current_field) > 0.01
            
        
        
        
        

        