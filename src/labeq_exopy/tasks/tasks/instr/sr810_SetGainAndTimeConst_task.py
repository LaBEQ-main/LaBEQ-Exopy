# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyHqcLegacy Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Task to configure a lock-in gain or time constant setting.

"""
import math
from atom.api import (Enum, Bool)
from exopy.tasks.api import InstrumentTask


class LockInSetGainAndTimeConstTask(InstrumentTask):
    """Configure a gain or time constant setting.

    """
    #initialize variables
    selected_sense=0
    selected_TimeConst=0
    SenseNum=0
    SenseMult=0
    SenseUnit=0
    TCNum=0
    TCMult=0
    TCUnit=0

    
    
    #: Values to be selected by the user: Boolean values used with checkbox UI
    AutoGain=Bool(False).tag(pref=True)

    SenseNum_1=Bool(False).tag(pref=True)
    SenseNum_2=Bool(False).tag(pref=True)
    SenseNum_3=Bool(False).tag(pref=True)
   
    SenseMult_1=Bool(False).tag(pref=True)
    SenseMult_2=Bool(False).tag(pref=True)
    SenseMult_3=Bool(False).tag(pref=True)

    SenseUnit_1=Bool(False).tag(pref=True)
    SenseUnit_2=Bool(False).tag(pref=True)
    SenseUnit_3=Bool(False).tag(pref=True)
    SenseUnit_4=Bool(False).tag(pref=True)
    
    TCNum_1=Bool(False).tag(pref=True)
    TCNum_2=Bool(False).tag(pref=True)
    
    TCMult_1=Bool(False).tag(pref=True)
    TCMult_2=Bool(False).tag(pref=True)
    TCMult_3=Bool(False).tag(pref=True)
    
    TCUnit_1=Bool(False).tag(pref=True)
    TCUnit_2=Bool(False).tag(pref=True)
    TCUnit_3=Bool(False).tag(pref=True)
    TCUnit_4=Bool(False).tag(pref=True)


    #Values to be selected by the user: String lists used in the drop down menu UI
    DynRes= Enum('Low','Normal','High','Auto').tag(pref=True)
    FltrSlope= Enum('6 dB','12 dB','18 dB','24 dB').tag(pref=True)
    SyncFltr= Enum('Off','Under200Hz').tag(pref=True)
    LineFltr= Enum('Out','Line','2xLine').tag(pref=True)


    def perform(self):
        #array of possible sensitivity values to chose from
        SenseList=[2*math.pow(10,-9),5*math.pow(10,-9),10*math.pow(10,-9),20*math.pow(10,-9),50*math.pow(10,-9),100*math.pow(10,-9),200*math.pow(10,-9),500*math.pow(10,-9),1*math.pow(10,-6),2*math.pow(10,-6),5*math.pow(10,-6),10*math.pow(10,-6),20*math.pow(10,-6),50*math.pow(10,-6),100*math.pow(10,-6),200*math.pow(10,-6),500*math.pow(10,-6),1*math.pow(10,-3),2*math.pow(10,-3),5*math.pow(10,-3),10*math.pow(10,-3),20*math.pow(10,-3),50*math.pow(10,-3),100*math.pow(10,-3),200*math.pow(10,-3),500*math.pow(10,-3)]
        
        #array of possible time constant values to chose from
        TimeConstList=[10*math.pow(10,-6),30*math.pow(10,-6),100*math.pow(10,-6),300*math.pow(10,-6),1*math.pow(10,-3),3*math.pow(10,-3),10*math.pow(10,-3),30*math.pow(10,-3),100*math.pow(10,-3),300*math.pow(10,-3),1,3,10,30,100,300,1*math.pow(10,3),3*math.pow(10,3),10*math.pow(10,3),30*math.pow(10,3)]
        
        #Dynamic Reserve settings selsection     
        if self.DynRes== 'Low':
            self.driver.set_dynres(2)
        elif self.DynRes== 'Normal':
            self.driver.set_dynres(1)
        elif self.DynRes== 'High':
            self.driver.set_dynres(0)
        elif self.DynRes== 'Auto':
            self.driver.set_dynres(3)
        
        #Filter Slope settings selection
        if self.FltrSlope== '6 dB':
            self.driver.set_fltrslope(0)
        elif self.FltrSlope== '12 dB':
            self.driver.set_fltrslope(1)
        elif self.FltrSlope== '18 dB':
            self.driver.set_fltrslope(2)
        elif self.FltrSlope== '24 dB':
            self.driver.set_fltrslope(3)
        
        #Line Filter settings selection
        if self.LineFltr== 'Out':
            self.driver.set_linefltr(0)
        elif self.LineFltr== 'Line':
            self.driver.set_linefltr(1)
        elif self.LineFltr== '2xLine':
            self.driver.set_linefltr(2)
        
        #Synchronous Filter settings selection
        if self.SyncFltr== 'Off':
            self.driver.set_syncfltr(0)
        elif self.SyncFltr== 'Under200Hz':
            self.driver.set_syncfltr(1)

        #Sensitivity settings selection
        if self.AutoGain == True:
            self.driver.set_sense(30)
        elif self.AutoGain == False:
            if self.SenseNum_1 == True:
                SenseNum=1
            elif self.SenseNum_2 == True:
                SenseNum=2
            elif self.SenseNum_3 == True:
                SenseNum=5

            if self.SenseUnit_1 == True:
                SenseUnit=1
                self.driver.set_sense(26)
            elif self.SenseUnit_2 == True:
                SenseUnit=math.pow(10,-3)
            elif self.SenseUnit_3 == True:
                SenseUnit=math.pow(10,-6)
            elif self.SenseUnit_4 == True:
               SenseUnit=math.pow(10,-9)

            if self.SenseMult_1 == True:
                SenseMult=1
            elif self.SenseMult_2 == True:
                SenseMult=10
            elif self.SenseMult_3 == True:
                SenseMult=100
            selected_sense=SenseNum*SenseMult*SenseUnit
        
            if SenseUnit != 1:
                for i in range (0,25):
                    if SenseList[i] == selected_sense:
                        self.driver.set_sense(i)

        #time constant settings selection
        if self.TCNum_1 == True:
            TCNum=1
        elif self.TCNum_2 == True:
            TCNum=3
        if self.TCUnit_1 == True:
            TCUnit=math.pow(10,3)
        elif self.TCUnit_2 == True:
            TCUnit=math.pow(10,0)
        elif self.TCUnit_3 == True:
            TCUnit=math.pow(10,-3)
        elif self.TCUnit_4 == True:
            TCUnit=math.pow(10,-6)

        if self.TCMult_1 == True:
            TCMult=1
        elif self.TCMult_2 == True:
            TCMult=10
        elif self.TCMult_3 == True:
            TCMult=100
        
        selected_TimeConst=TCNum*TCMult*TCUnit

        for i in range(0,19):
            if TimeConstList[i] == selected_TimeConst:
                self.driver.set_timeconst(i)