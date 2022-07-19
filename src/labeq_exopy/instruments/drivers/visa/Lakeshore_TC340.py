# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Authors - Kathryn Evancho, LaBEQ / Sardashti Research Group, Clemson University
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------

"""Drivers for Lakeshore 340 Temperature Controller using VISA library.

"""
from ..driver_tools import (InstrIOError)
from ..visa_tools import VisaInstrument

#note: 
#termination requirements unclear. Addition of a termination character at the end of each 
# command may be nesessary. For now, it is operational without terminaiton
#(see lakeshore 340 temperature controller manual)

class LakeshoreTC340(VisaInstrument):

    def open_connection(self, **para):
        #Open the connection to the instr using the `connection_str`.
        super(LakeshoreTC340, self).open_connection(**para)
        self.write_termination = '\n'
        self.read_termination = '\n'
    
    def set_loop_limits(self, limits):
        """CLIMIT handels all limit settings for loop 1 or 2:
            setpoint limit/loop cutoff, max positive change in output, max negative change in output, 
            max current, max heater range """

        self.write('CLIMIT ' + str(limits))

    def set_heater_range(self,range):
        "Sets Heater Range to 'off' or one of the output values"
        
        self.write('RANGE ' + str(range))

    def configure_control(self, parameters):
        """CSET configures the control loop parameters of loop 1 or 2:
            control channel, setpoint units, on/off, on/off on startup"""
            
        self.write('CSET ' + str(parameters))
    
    def measure_temperature(self,input):
        """ Returns the temperature reading the selected input in kelvin """
        #note:
        #The RDGST? funciton was used to match the errors displayed on the instrument screen.
        #Using the KRDG? function without RDGST? works just as well.
        #Using RDGST? provides the user with more information than the KRDG? funciton can alone.

        bit_weighting =self.query('RDGST? '+ str(input))
        
        if(float(bit_weighting) == 0):
            K = self.query('KRDG? ' + str(input))
            return K
        elif(float(bit_weighting) == 1):
            raise InstrIOError('TC340: Invalid Reading')
        elif(2 <= float(bit_weighting) < 16):
            raise InstrIOError('TC340: Old Reading')
        elif( 16 <= float(bit_weighting) < 32):
            raise InstrIOError('TC340: T-UNDER')
        elif( 32 <= float(bit_weighting) < 64):
            raise InstrIOError('TC340: T-OVER')
        elif( 64 <= float(bit_weighting) < 128):
            raise InstrIOError('TC340: S-ZERO')
        elif( 128 <= float(bit_weighting)):
            raise InstrIOError('TC340: S-OVER')
        else:
            raise InstrIOError('TC340: Measurement Failed')
    
    def set_PID(self,Auto, pid):
        """ Sets the PID values of the selected loop or sets to AUTO PID"""
        #note: 
        #This was made to chose between full auto or full manual PID.
        #There are other options under the CMODE function which are not included here.
        #(see Lakeshore 340 temperature controller manual)

        if(Auto == True):
            self.write('CMODE 4')
        else:
            self.write('CMODE 1')
            self.write('PID ' + str(pid))
    
    def set_mout(self,val):
        """Sets the manual output percentage """
        
        self.write('MOUT ' + str(val))
    
    def set_setpoint(self, loop, val):
        """sets the heater setpoint """

        self.write('SETP ' + str(loop) + ',' + str(val))
    
    def input_settings(self, settings):
        """The INTYPE command controlls all of the input settings for A or B: 
            Diode type, Units, Coefficient, Excitation, Range"""
        #note:
        #The INTYPE options after the 'Diode type' setting are diode specific.
        #They autoset based off the 'Diode type' selection
        #The settings can be manually altered if desired using the next 4 setting options
        #The task file for this driver only prompts the user for the first two inputs

        self.write('INTYPE ' + str(settings))

    def set_input_curve(self, input, curve):
        """sets the diode curve """
        #note:
        #The curves are diode specific.
        #Correction for this is included in the corresponding task file

        self.write('INCRV ' + str(input) + ',' + str(curve))
    
    def LoopONCheck(self,loop):
        "Returns a loop's on or off status: 1 = On, 0 = Off"

        
        loop_parameters = self.write('CSET? ' + str(loop))
        loop_parameters_str = str(loop_parameters)
        loop_parameters_arr = loop_parameters_str.split(',')

        return int(loop_parameters_arr[3])
