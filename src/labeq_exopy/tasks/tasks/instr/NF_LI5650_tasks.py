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

class NFLockInMeasureTask(InstrumentTask):
    """ Measure lock in output"""

    # Time to wait before execution
    wait_time = Float().tag(pref=True)

    val = Enum('R', 'Phase', 'X', 'Y').tag(pref=True)
    wait = set_default({'activated': True, 'wait': ['instr']})
    database_entries = set_default({'val': 0.0})

    def perform(self):
        
        sleep(self.wait_time)

        num = self.driver.measure(self.val)
        self.write_in_database('val', num)


class SetSensAndDynResrvTask(InstrumentTask):
    """ Sets sensitivity mode. OFF - sensitivity and dynamic reserve chosen by device. ON - chosen by user."""

    # Time to wait before execution
    wait_time = Float().tag(pref=True)

    sensitivity = Str().tag(pref=True)
    dynres = Enum('LOW', 'MED', 'HIGH').tag(pref=True)
    mode = Enum('OFF', 'ON').tag(pref=True)

    wait = set_default({'activated': True, 'wait': ['instr']})
    
    database_entries = set_default({'val': 0.0})
    database_entries = set_default({'mode': 'none'})

    def perform(self):
        
        sleep(self.wait_time)

        if self.mode == "OFF":
            val = self.format_and_eval_string(self.sensitivity)
            
            self.driver.set_sensitivity(val)
            self.driver.set_dynres(self.dynres)
            self.write_in_database('val', val)
        elif self.mode == "ON":
            self.driver.set_sens_mode(self.mode)
            self.write_in_database('mode', self.mode)

class SetTimeConstantTask(InstrumentTask):
    """ Sets time constant (s) and slope (dB)"""

    # Time to wait before execution
    wait_time = Float().tag(pref=True)

    tc = Str().tag(pref=True)
    slope = Enum('6', '12', '18', '24').tag(pref=True)
    
    wait = set_default({'activated': True, 'wait': ['instr']})

    def perform(self):
        
        sleep(self.wait_time)

        tc = self.format_and_eval_string(self.tc)
        self.driver.set_tc(tc)

        slope = self.format_and_eval_string(self.slope)
        self.driver.set_tc_slope(slope)

class SetInputAndRefTask(InstrumentTask):
    """ Sets time constant (s) and slope (dB)"""

    # Time to wait before execution
    wait_time = Float().tag(pref=True)

    
    input = Enum('A', 'AB', 'I').tag(pref=True)
    coupling = Enum('AC', 'DC').tag(pref=True)
    refsource = Enum('INT OSC', 'REF IN', 'SIGNAL').tag(pref=True)
    RefInType = Enum('SIN', 'TPOS', 'TNEG').tag(pref=True)
    IntOscFreq = Str().tag(pref=True)
    IntOscAmp = Str().tag(pref=True)
    IntOscRange = Str().tag(pref=True)
    RefSigPhaseShift = Str().tag(pref=True)

    wait = set_default({'activated': True, 'wait': ['instr']})
    
    database_entries = set_default({'input': ''})
    database_entries = set_default({'coupling': ''})
    database_entries = set_default({'refsource': ''})
    database_entries = set_default({'RefInType': ''})
    database_entries = set_default({'IntOscFreq': ''})
    database_entries = set_default({'IntOscAmp': ''})
    database_entries = set_default({'IntOscRange': ''})
    database_entries = set_default({'RefSigPhaseShift': ''})

    def perform(self):
        
        sleep(self.wait_time)

        input = self.input
        self.driver.set_sig_input(input)
        self.write_in_database('input', input)

        coupling = self.coupling
        self.driver.set_input_coup(coupling)
        self.write_in_database('coupling', coupling)

        refsource = self.refsource
        self.driver.set_ref_sig(refsource)
        self.write_in_database('refsource', refsource)

        if refsource == 'REF IN':
            RefInType = self.RefInType
            self.driver.set_refin_type(RefInType)
            self.write_in_database('RefInType', RefInType)
        
        if refsource == 'INT OSC':

            #set int osc freq
            IntOscFreq = self.format_and_eval_string(self.IntOscFreq)
            self.driver.set_psd1_freq(IntOscFreq)
            self.write_in_database('IntOscFreq', IntOscFreq)

            #set int osc amplitude
            IntOscAmp = self.format_and_eval_string(self.IntOscAmp)
            self.driver.set_psd1_amp(IntOscAmp)
            self.write_in_database('IntOscAmp', IntOscAmp)

            #set int osc range
            IntOscRange = self.format_and_eval_string(self.IntOscRange)
            self.driver.set_psd1_range(IntOscRange)
            self.write_in_database('IntOscRange', IntOscRange)

        RefSigPhaseShift = self.format_and_eval_string(self.RefSigPhaseShift)
        self.driver.set_psd1_phase(RefSigPhaseShift)
        self.write_in_database('RefSigPhaseShift', RefSigPhaseShift)
