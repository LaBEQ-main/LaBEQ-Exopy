# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyHqcLegacy Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Task to configure a lock-in input or reference setting.

"""
from atom.api import (Enum, Bool, Str)
from exopy.tasks.api import InstrumentTask


class LockInSetInputAndRefTask(InstrumentTask):
    """Configure the lock-in input and reference

    """
    #: Value to retrieve.
    Reference=Enum('Int','Ext').tag(pref=True)
    Ground=Enum('GND','Float').tag(pref=True)
    Inputs=Enum('A','A-B','I1M\u03A9','I100M\u03A9').tag(pref=True)
    
    #User input
    AutoPhase=Bool(False).tag(pref=True)
    input_frequency=Str().tag(pref=True)
    input_phase=Str().tag(pref=True)
    input_amplitude=Str().tag(pref=True)
    
    def perform(self):
        
        if self.AutoPhase:
            self.driver.set_phase(800)
        else:
            self.driver.set_phase(self.input_phase)
        
        if self.Reference == 'Int':
            self.driver.set_reference(1)
            self.driver.set_frequency(self.input_frequency)
            self.driver.set_amplitude(self.input_amplitude)
        elif self.Reference == 'Ext':
            self.driver.set_reference(0)
        
        if self.Ground == 'GND':
            self.driver.set_ground(1)
        elif self.Ground == 'Float':
            self.driver.set_ground(0)
        
        if self.Inputs =='A':
            self.driver.set_input(0)
        elif self.Inputs == 'A-B':
            self.driver.set_input(1)
        elif self.Inputs == 'I1M\u03A9':
            self.driver.set_input(2)
        elif self.Inputs == 'I100\u03A9':
            self.driver.set_input(3)


