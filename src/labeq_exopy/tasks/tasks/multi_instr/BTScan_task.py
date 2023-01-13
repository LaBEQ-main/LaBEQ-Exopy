# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Authors - Frank Duffy, LaBEQ / Sardashti Research Group, Clemson University
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
import numpy as np
import math, time, csv
from tabulate import tabulate
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

        print(self.temp_max)
        print(self.temp_min)
        print(self.temp_step)

        # calculate number of temp steps
        total_temp_steps = math.floor(np.absolute(self.temp_max - self.temp_min)/self.temp_step)
        print(total_temp_steps)

        # get start time in linux format and save to db
        start_time = timer.initiate_timer()
        self.write_in_database('start_time', start_time)

        # set up save file with headers

        # check that the probe temp is steadystate at the set point. timeout error or timeout continue?
        # Ramp field to min if it's not already there. Field always starts at field_min.

        # time to wait for probe to steady out
        probe_wait_time = 10

        # open files for storing data
        probe_monitor_file = open(self.directory + "/probe_monitor.txt", "a")

        # initialize data storage files
        headers =   [
                        'task time (s)', 
                        "monitor time (s)", 
                        'probe temp (K)'
                    ]
        
        # create DictWriter and write the header to the probe monitor file
        writer = csv.DictWriter(probe_monitor_file, headers, delimiter='\t')
        writer.writeheader()

        # create list to store probe temperature monitor data for the duration of the experiment
        probe_monitor_data = []

        # main experiment loop
        for i in range(total_temp_steps + 1):

            probe_set_time = self.set_probe_temp(i)

            # start timer
            elapsed_time = 0

            # output header to subprocess panel for live data monitoring
            print('time (s), probe temp (K)')

            # monitor the temperature for the prescribed number of seconds
            while(elapsed_time < probe_wait_time):
                
                # get time since experiment began
                task_time = timer.get_elapsed_time()

                # calculate time since monitor began
                elapsed_time = round(time.time() - probe_set_time, 3)

                # measure the probe temperature
                probe_temp = 1.5 # itc.read_probe_temp()

                # print elapsed time and current probe temperature
                print(str(elapsed_time) + ',' + str(probe_temp))
                
                # assemble the row dict to be saved to text and stored in the overall dataset
                row =   {
                            "task time (s)": task_time, 
                            "monitor time (s)": elapsed_time, 
                            "probe temp (K)": probe_temp
                        }

                # save to specified text file
                writer.writerow(row)

                # append row to probe monitor dataset
                probe_monitor_data.append(row)

                # sleep 1 second to improve performance.
                sleep(1)


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
            
    def set_probe_temp(self, i):
        """ 
            sets the probe temperature and returns the set time 

        """

        #calculate the temperature set point
        temp_setpoint = self.temp_min + i *self.temp_step
        print("Setting probe temperature to : " + str(temp_setpoint) + "K")

        # set the probe to the temperature set point
        # itc.set_probe_temp(temp_setpoint)

        # note the time when the probe setpoint was made for calculating the elapsed time later
        probe_set_time = time.time()
        return probe_set_time
        

        