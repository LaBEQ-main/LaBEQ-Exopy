# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyHqcLegacy Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Drivers for Stanford instrument lock-in SR810 using VISA library.

"""
#I do not know how this got there:
#from this import d
from ..driver_tools import (InstrIOError, secure_communication)
from ..visa_tools import VisaInstrument


class LockInSR530(VisaInstrument):
    """Driver for a SR530 lock-in, using the VISA library.

    This driver does not give access to all the functionnality of the
    instrument but you can extend it if needed. See the documentation of
    the driver_tools module for more details about writing instruments
    drivers.

    Parameters
    ----------
    see the `VisaInstrument` parameters in the `driver_tools` module

    Methods
    -------
    read_x()
        Return the x quadrature measured by the instrument
    read_y()
        Return the y quadrature measured by the instrument
    read_xy()
        Return the x and y quadratures measured by the instrument
    read_amplitude()
        Return the ammlitude of the signal measured by the instrument
    read_phase()
        Return the phase of the signal measured by the instrument
    read_amp_and_phase()
        Return the amplitude and phase of the signal measured by the instrument
    read_frequency()
        Return the frequency measured by the instrument
    """

    def __init__(self, *args, **kwargs):

        super(LockInSR530, self).__init__(*args, **kwargs)
        bus = kwargs.get('bus', 'GPIB')
        if bus == 'GPIB':
            self.write('OUTX1')
        elif bus == 'RS232':
            self.write('OUTX0')
        else:
            raise InstrIOError('In invalib bus was specified')

    @secure_communication()
    def read_x(self):
        """
        Return the x quadrature measured by the instrument
        """
        self.write('S, 0')
        value = self.query('Q1')
        if not value:
            raise InstrIOError('The command did not complete correctly')
        else:
            return float(value)
    
    @secure_communication()
    def read_y(self):
        """
        Return the y quadrature measured by the instrument
        """
        self.write('S, 0')
        value = self.query('Q2')

        if not value:
            raise InstrIOError('The command did not complete correctly')
        else:
            return float(value)
        
    @secure_communication()
    def read_xy(self):
        """
        Return the x and y quadratures measured by the instrument
        """

        self.write('S, 0')
        values = self.query('S')

        if not values:
            raise InstrIOError('The command did not complete correctly')
        else:
            return values

    @secure_communication()
    def read_amplitude(self):
        """
        Return the amplitude of the signal measured by the instrument
        """
        self.write('S, 2')
        value = self.query('Q1')

        if not value:
            return InstrIOError('The command did not complete correctly')
        else:
            return float(value)

    @secure_communication()
    def read_theta(self):
        """
        Return the phase difference of the signal measured by the instrument

        """
        #Note: This function reads the MEASURED phase value
        
        self.write('S, 2')
        value = self.query('Q2')

        if not value:
            raise InstrIOError('The command did not complete correctly')
        else:
            return float(value)

    @secure_communication()
    def read_amp_and_theta(self):
        """
        Return the amplitude and phase difference of the signal measured by the instrument
        """
        self.write('S, 2')
        values = self.query('S')

        if not values:
            raise InstrIOError('The command did not complete correctly')
        else:
            return values

    @secure_communication()
    def read_frequency(self):
        """
        Return the frequency of the signal measured by the instrument
        """
        value = self.query('F')
        if not value:
            raise InstrIOError('The command did not complete correctly')
        else:
            return float(value)
    
    @secure_communication()
    def read_phase(self):
        """
        Return the phase of the signal measured by the instrument
        """
        #Note: this function returns the phase setting NOT the measured phase
        
        value = self.query('P')
        
        if not value:
            raise InstrIOError('The command did not complete correctly')
        else:
            return float(value)
    
    @secure_communication()
    def set_phase(self,x):
        """
        Set the phase of the instrument

        """
        if x == 800:
            value = self.write('APHS')
        else:
            str1='PHAS '
            index = str1.find('PHAS ')
            input = str1[index:] + str(x)
            value = self.write(input)

        check='check'
        if type(value) == type(check):
            raise InstrIOError('The command did not complete correctly')
        else:
            return 'completed'

    @secure_communication()
    def set_frequency(self,f):
        """
        Set the frequency of the instrument

        """
        #Note: The frequency for the SR530 is controlled by the analog X6 output
        #The scale is found and then applied to the inputted f to select the correct frequency
        str1='FREQ '
        index = str1.find('FREQ ')
        input = str1[index:] + str(f)
        value = self.write(input)

        check='check'
        if type(value) == type(check):
            raise InstrIOError('The command did not complete correctly')
        else:
            return 'completed'

    @secure_communication()
    def set_amplitude(self,x):
        #The SR530 does not have a function to set the amplitude
        #This is done manually with the switch and calibration screw on the back of the LIA
        return 'n/a'
    
    @secure_communication()
    def set_timeconst(self,i):
        """
        Set the time constant of the instrument

        """
        #Note: This function is made to work with the existing task and view files for the other SR LIA's.
        #The time constant range for this model is smaller than the others. This is compensated for below.

        if i < 4:
            print('Time constant out of range: too high! Time constat set to 1ms')
            value = self.write('T 1,1')
        elif i > 14:
            print('Time constant out of range: too low! Time constant set to 100s')
            value = self.write('T 1,11')
        else:
            n = i-3
            value = self.write('T 1,'+ str(n))
        
        #None: The command below sets the post TC to 'none'
        #there are options of 0.1 and 1 second if desired (see SR530 Manual)
        self.write('T 2,0')
        
        print(str(i))

        check='check'
        if type(value) == type(check):
            raise InstrIOError('The command did not complete correctly')
        else:
            return 'completed'
    
    @secure_communication()
    def set_sense(self,i):
        """
        Return the sensitivity of the instrument (No auto option)

        """
        #Note: This function is made to work with the existing task and view files for the other SR LIA's.
        #The sensitivty range for this model is smaller than the others. This is compensated for below.
        n=1

        if i < 2:
            print('Sensitivity out of range: too high! Sensitivity set to 10nV')
            value = self.write('G 1')
        elif i > 25:
            print('Sensitivity out of range: too low! Sensitivity set to 500mV')
            value = self.write('G 2')
        else:
            n = i-1
            value = self.write('G'+ str(n))

        #Check to ensure the sensitivity is not overloaded
        ch1_meter = self.query('QX')
        while float(ch1_meter) >= 8:
            print('Overload! Reducing sensitivity...')
            n = n-1
            if n < 1:
                raise InstrIOError('The command did not complete correctly: No sensitivty found!')
            self.write('G'+ str(n))
            ch1_meter = self.query('QX')

        print(str(i)+','+str(n))

        check='check'
        if type(value) == type(check):
            raise InstrIOError('The command did not complete correctly')
        else:
            return 'completed'

    @secure_communication()
    def set_dynres(self,i):
        """
        Set the dynamic reserve of the instrument

        """

        #Note: This function is made to work with the existing task and view files for the other SR LIA's.
        #The dynamic reserve settings are reversed for the other SR LIA's (0=high, 2=low)
        #This is compensated for below

        if i == 0:
            n = 2
        elif i == 2:
            n = 0
        else:
            n = 1

        value = self.write('D ' + str(n))
        check='check'
        if type(value) == type(check):
            raise InstrIOError('The command did not complete correctly')
        else:
            return 'completed'

    @secure_communication()
    def set_syncfltr(self,i):
        """
        set the sync filter

        """
        #Note: For the SR530 this function corresponds to the 'bandpass filter'
        value = self.write('B'+str(i))

        check='check'
        if type(value) == type(check):
            raise InstrIOError('The command did not complete correctly')
        else:
            return 'completed'
    
    @secure_communication()
    def set_fltrslope(self,i):
        #There is no low pass filter option for the SR530
        return 'n/a'

    @secure_communication()
    def set_linefltr(self,i):
        """
        set the line filter

        """
        if i == 0:
            self.write('L 1,0')
            self.write('L 2,0')
        elif i == 1:
            self.write('L 1,1')
            self.write('L 2,0')
        elif i == 2:
            self.write('L 2,1')
            self.write('L 1,0')
        elif i ==3:
            self.write('L 1,1')
            self.write('L 2,1')
        print (str(i))
    
    @secure_communication()
    def set_input(self, i):
        #No option for SR530 LIA
        return 'n/a'
    
    @secure_communication()
    def set_ground(self,i):
        #No option for SR530 LIA
        return 'n/a'
    @secure_communication()
    def set_reference(self,i):
        #No Option for SR530 LIA
            
        return 'n/a'
    

