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


class LockInEGGPAR5210(VisaInstrument):
    """Driver for a SR810 lock-in, using the VISA library.

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

        super(LockInSR810, self).__init__(*args, **kwargs)
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

        Perform a direct reading without any waiting. Can return non
        independent values if the instrument is queried too often.

        """
        value = self.query('OUTP?1')
        if not value:
            raise InstrIOError('The command did not complete correctly')
        else:
            return float(value)
    
    @secure_communication()
    def read_y(self):
        """
        Return the y quadrature measured by the instrument

        Perform a direct reading without any waiting. Can return non
        independent values if the instrument is queried too often.

        """
        value = self.query('OUTP?2')
        if not value:
            raise InstrIOError('The command did not complete correctly')
        else:
            return float(value)
        
    @secure_communication()
    def read_xy(self):
        """
        Return the x and y quadratures measured by the instrument

        Perform a direct reading without any waiting. Can return non
        independent values if the instrument is queried too often.

        """
        values = self.query_ascii_values('SNAP?1,2')
        if not values:
            raise InstrIOError('The command did not complete correctly')
        else:
            return values

    @secure_communication()
    def read_amplitude(self):
        """
        Return the amplitude of the signal measured by the instrument

        Perform a direct reading without any waiting. Can return non
        independent values if the instrument is queried too often.

        """
        value = self.query('OUTP?3')
        if not value:
            return InstrIOError('The command did not complete correctly')
        else:
            return float(value)

    @secure_communication()
    def read_theta(self):
        """
        Return the phase difference of the signal measured by the instrument

        Perform a direct reading without any waiting. Can return non
        independent values if the instrument is queried too often.

        """
        value = self.query('OUTP?4')
        if not value:
            raise InstrIOError('The command did not complete correctly')
        else:
            return float(value)

    @secure_communication()
    def read_amp_and_theta(self):
        """
        Return the amplitude and phase difference of the signal measured by the instrument

        Perform a direct reading without any waiting. Can return non
        independent values if the instrument is queried too often.

        """
        values = self.query_ascii_values('SNAP?3,4')
        if not values:
            raise InstrIOError('The command did not complete correctly')
        else:
            return values

    @secure_communication()
    def read_frequency(self):
        """
        Return the frequency of the signal measured by the instrument

        Perform a direct reading without any waiting. Can return non
        independent values if the instrument is queried too often.

        """
        value = self.query('FREQ?')
        if not value:
            raise InstrIOError('The command did not complete correctly')
        else:
            return float(value)
    @secure_communication()
    def read_phase(self):
        """
        Return the phase of the signal measured by the instrument

        Perform a direct reading without any waiting. Can return non
        independent values if the instrument is queried too often.

        """
        value = self.query('PHAS?')
        if not value:
            raise InstrIOError('The command did not complete correctly')
        else:
            return float(value)
    #In the following section, auto settings are selected when the function input is
    #given a distinct value outside of the maunal funciton input range
    #many of the settings take in user input to set to a certaint value

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
        """
        Set the amplitude of the internal ossilator

        """
        str1='SLVL '
        index = str1.find('SLVL ')
        input = str1[index:] + str(x)
        value = self.write(input)

        check='check'
        if type(value) == type(check):
            raise InstrIOError('The command did not complete correctly')
        else:
            return 'completed'
    @secure_communication()
    def set_timeconst(self,i):
        """
        Set the time constant of the instrument

        """
        str1='OFLT '
        index = str1.find('OFLT ')
        input = str1[index:] + str(i)
        value = self.write(input)

        check='check'
        if type(value) == type(check):
            raise InstrIOError('The command did not complete correctly')
        else:
            return 'completed'
    @secure_communication()
    def set_sense(self,i):
        """
        Return the sensitivity of the instrument (auto or manual)

        """
        if i == 30:
            value = self.write('AGAN')
        else:
            str1='SENS '
            index = str1.find('SENS ')
            input = str1[index:] + str(i)
            value = self.write(input)
            print(input)

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
        if i == 3:
            value = self.write('ARSV')
        else:
            str1='RMOD '
            index = str1.find('RMOD ')
            input = str1[index:] + str(i)
            value = self.write(input)
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
        str1='SYNC '
        index = str1.find('SYNC ')
        input = str1[index:] + str(i)
        value = self.write(input)

        check='check'
        if type(value) == type(check):
            raise InstrIOError('The command did not complete correctly')
        else:
            return 'completed'
    @secure_communication()
    def set_fltrslope(self,i):
        """
        set the filter slope

        """
        str1='OFSL '
        index = str1.find('OFSL ')
        input = str1[index:] + str(i)
        value = self.write(input)

        check='check'
        if type(value) == type(check):
            raise InstrIOError('The command did not complete correctly')
        else:
            return 'completed'
    @secure_communication()
    def set_linefltr(self,i):
        """
        set the line filter

        """
        str1='ILIN '
        index = str1.find('ILIN ')
        input = str1[index:] + str(i)
        value = self.write(input)
        
        check='check'
        if type(value) == type(check):
            raise InstrIOError('The command did not complete correctly')
        else:
            return 'completed'
    @secure_communication()
    def set_input(self, i):
        """
        Set the Signal Input

        """
        str1='ISRC '
        index = str1.find('ISRC ')
        input = str1[index:] + str(i)
        value = self.write(input)

        check='check'
        if type(value) == type(check):
            raise InstrIOError('The command did not complete correctly')
        else:
            return 'completed'
    
    @secure_communication()
    def set_ground(self,i):
        """
        set the ground

        """
        str1='IGND '
        index = str1.find('IGND ')
        input = str1[index:] + str(i)
        value = self.write(input)

        check='check'
        if type(value) == type(check):
            raise InstrIOError('The command did not complete correctly')
        else:
            return 'completed'
    @secure_communication()
    def set_reference(self,i):
        """
        set the reference to external or internal

        """
        str1='FMOD '
        index = str1.find('FMOD ')
        input = str1[index:] + str(i)
        value = self.write(input)
        
        check='check'
        if type(value) == type(check):
            raise InstrIOError('The command did not complete correctly')
        else:
            return 'completed'
    

