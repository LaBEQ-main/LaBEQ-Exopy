# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Authors - Kathryn Evancho, LaBEQ / Sardashti Research Group, Clemson University
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------

"""Tasks to control the Lakeshore TC340

"""
from cmath import sin
from this import d
from time import sleep

from atom.api import (Enum, Float, set_default,Bool,Str)

from exopy.tasks.api import InstrumentTask

class LakeshoreTC340MeasureTask(InstrumentTask):
    #: Input value to retrieve.
    MeasInput = Enum('A', 'B').tag(pref=True)
    
    #: Time to wait before performing the measurement.
    #waiting_time = Float().tag(pref=True)

    database_entries = set_default({'A': 1.0})

    #wait = set_default({'activated': True, 'wait': ['instr']})

    def perform(self):
        """Wait and query the last value in the instrument buffer.

        """
        #sleep(self.waiting_time)
        #measurement selection
        if self.MeasInput == 'A':
            value = self.driver.measure_temperature(self.MeasInput)
            self.write_in_database('A', value)
        elif self.MeasInput == 'B':
            value = self.driver.measure_temperature(self.MeasInput)
            self.write_in_database('B', value)
    
    def _post_setattr_MeasInput(self, old, new):
        """ Update the database entries acording to the MeasInput.
        """
        entries = self.database_entries.copy()
        for k in ('A', 'B'):
            if k in entries:
                del entries[k]
        if new == 'A':
            entries['a'] = 1.0
        elif new == 'B':
            entries['b'] = 1.0
        self.database_entries = entries

class LakeshoreTC340ConfigureTask(InstrumentTask):
    #: Selected Loop.
    Loop = Enum('1', '2').tag(pref=True)
    SetPointLimit = Float(475).tag(pref=True)
    PosSlopeMax = Float().tag(pref=True)
    NegSlopeMax = Float().tag(pref=True)
    HtrRes = Float(25).tag(pref=True)
    MaxCurr = Enum('0.25A', '0.5A', '1A','2A').tag(pref=True)
    MaxHtrRange = Enum('Full', '1/10','1/10\u00b2', '1/10\u00b3','1/10\u2074', 'OFF').tag(pref=True)
    SetHtrRange = Enum('Full','1/10','1/10\u00b2', '1/10\u00b3','1/10\u2074', 'OFF').tag(pref=True)
    CntrlChannel = Enum('A','B').tag(pref=True)
    SetpUnits = Enum('K', 'C', 'Sensor').tag(pref=True)
    AutoPID = Bool(False).tag(pref=True)
    P = Float(50).tag(pref=True)
    I = Float(20).tag(pref=True)
    D = Float(13).tag(pref=True)
    Mout = Float().tag(pref=True)
    SetPoint = Float(300).tag(pref=True)
    ConfigInput = Enum('A','B').tag(pref=True)
    Diode = Enum('Silicon', 'Platinum 100 (250\u03A9)', 'Platinum 100 (500\u03A9)','Platinum 1000').tag(pref=True)
    Curve = Enum('No Curve','DT-470','DT-500-D','DT-500-E1','DT-670','PT-100','PT-1000').tag(pref=True)


    #: Time to wait before performing the measurement.
    #waiting_time = Float().tag(pref=True)

    database_entries = set_default({'A': 1.0})

    #wait = set_default({'activated': True, 'wait': ['instr']})
    
    def perform(self):
        """Wait and query the last value in the instrument buffer.
        
        """
        #sleep(self.waiting_time)

        #selection of dioden type:
        if self.Diode == 'Silicon':
            diode = '1'
        elif self.Diode == 'Platinum 100 (250\u03A9)':
            diode = '3'
        elif self.Diode == 'Platinum 100 (500\u03A9)':
            diode = '4'
        elif self.Diode == 'Platinum 1000':
            diode = '5'
        
        #Sending input settings information
        self.driver.input_settings(self.ConfigInput + ',' + diode)

        #Selection of diode curve
        if self.Curve == 'No Curve':
            curve = '0'
        elif self.Curve == 'DT-470':
            curve = '1'
        elif self.Curve == 'DT-500-D':
            curve = '2'
        elif self.Curve == 'DT-500-E1':
            curve = '3'
        elif self.Curve == 'DT-670':
            curve = '11'
        elif self.Curve == 'PT-100':
            curve = '4'
        elif self.Curve == 'PT-1000':
            curve = '5'

        #Check if curve is appropriate for diode.
        #If an invalid curve is selected the curve setting defaults to 'No Curve'
        #If the curve is applicable for the diode, that curve will be set.
        if (diode == '1' and (curve == '4' or curve == '5')) or (diode !='1' and (curve == '1' or curve == '2' or curve == '3' or curve == '11')):
            print('Invalid Curve! No Curve Set')
            self.driver.set_input_curve(self.ConfigInput, 0)
        else:
            self.driver.set_input_curve(self.ConfigInput, curve)

        #Setpoint Units Selection and Input Settings Command
        if self.SetpUnits == 'K':
            parameters = self.Loop + ',' + self.CntrlChannel + ',' + '1,1,1'
            self.driver.configure_control(parameters)
        elif self.SetpUnits == 'C':
            parameters = self.Loop + ',' + self.CntrlChannel + ',' + '2,1,1'
            self.driver.configure_control(parameters)
        elif self.SetpUnits == 'Sensor':
            parameters = self.Loop + ',' + self.CntrlChannel + ',' + '3,1,1'
            self.driver.configure_control(parameters)
        
        #Check to make sure only one loop is turned on.
        #If both are on, the unselected loop will be turned off
        if self.Loop == 1:
            Loop = 2
            self.driver.TurnLoopOff(Loop)
        else:
            Loop = 1
            self.driver.TurnLoopOff(Loop)
        

        #PID Settings: Switches between Auto and Manual
        if self.AutoPID:
            pid = 0
            self.driver.set_PID(self.AutoPID, str(pid))
        else:
            pid_arr = [self.Loop,self.P,self.I,self.D]
            pid = ','.join(str(i) for i in pid_arr)
            self.driver.set_PID(self.AutoPID, str(pid))
        
        #Set Mout value
        mout_input = str(self.Loop) + ',' + str(self.Mout)
        self.driver.set_mout(mout_input)

        #Configure loop limits
        limits_arr = [self.Loop, self.SetPointLimit, self.PosSlopeMax, self.NegSlopeMax, self.MaxCurr, self.MaxHtrRange]
        limits = ','.join(str(i) for i in limits_arr)
        self.driver.set_loop_limits(limits)

        #Set Heater Resistance
        self.driver.set_heater_resistance(self.Loop,self.HtrRes)
        
        #Set Setpoint
        self.driver.set_setpoint(self.Loop,self.SetPoint)




    

        

    