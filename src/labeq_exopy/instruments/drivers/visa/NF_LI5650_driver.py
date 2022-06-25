# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Authors - Frank Duffy, LaBEQ / Sardashti Research Group, Clemson University
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------

"""Drivers for NF LI5650 lock-in amplifier using VISA library.

"""
from ..driver_tools import (InstrIOError, secure_communication, instrument_property)
from ..visa_tools import VisaInstrument


class LI5650(VisaInstrument):
    """NF LI5650 lock-in amplifier. """

    def open_connection(self, **para):
        """Open the connection to the instr using the `connection_str`.

        """
        super(LI5650, self).open_connection(**para)
        self.write_termination = '\n'
        self.read_termination = '\n'

    def measure(self, val):
        """ set sensitivity mode """
        
        #first make sure data output format is DATA1,DATA2,DATA3,DATA4
        self.write('DATA 30')
        
        #now ensure data outputs are R,Phase,X,Y
        self.write('CALC1:FORM MLIN')
        self.write('CALC2:FORM PHAS')
        self.write('CALC3:FORM REAL')
        self.write('CALC4:FORM IMAG')

        #get data
        data = (self.query('FETC?')).split(',')

        #measure the specified value
        if val == 'R':
            return data[0]
        elif val == 'Phase':
            return data[1]
        elif val == 'X':
            return data[2]
        elif val == 'Y':
            return data[3]

    def set_sens_mode(self, mode):
        """ set sensitivity mode """
        
        self.write('SENS:VOLT:AC:RANG:AUTO ' + str(mode))

    def set_dynres(self, mode):
        """ set dynamic reserve low/med/high """

        self.write('SENS:DRES ' + str(mode))

    def set_sensitivity(self, val):
        """ set sensitivity range 10E-9 to 1, 1-2-5 sequence, unit Vrms """

        self.write('SENS:VOLT:AC:RANG:UPP ' + str(val))

    def set_tc(self, val):
        """set time constant """

        self.write('SENS:FILT:LPAS:TCON ' + str(val))
    
    def set_tc_slope(self, val):
        """set time constant """

        self.write('SENS:FILT:LPAS:SLOP ' + str(val))
    
    def set_sig_input(self, val):
        """set signal input"""

        self.write('ROUT:TERM ' + str(val))

    def set_input_coup(self, val):
        """set input coupling """

        self.write('INP:COUP ' + str(val))

    def set_ref_sig(self, val):
        """set reference signal """

        if val == "REF IN":
            self.write('ROUT2:TERM RINP')
        elif val == "INT OSC":
            self.write('ROUT2:TERM IOSC')
        elif val == "SIGNAL":
            self.write('ROUT2:TERM SINP')
    
    def set_refin_type(self, val):
        """set reference input type """
        
        if val == "SIN":
            self.write('INP2:TYPE SIN')
        elif val == "TPOS":
            self.write('INP2:TYPE TPOS')
        elif val == "TNEG":
            self.write('INP2:TYPE TNEG')
    
    def set_psd1_freq(self, val):
        """set psd1 freq"""
        
        self.write('SOUR:FREQ ' +str(val))
    
    def set_psd1_amp(self, val):
        """set psd1 amp"""
        
        self.write('SOUR:VOLT ' +str(val))

    def set_psd1_range(self, val):
        """set psd1 amp"""
        
        self.write('SOUR:VOLT:RANG ' +str(val))

    def set_psd1_phase(self, val):
        """set psd1 phase"""
        
        self.write('SENS:PHAS ' +str(val))
