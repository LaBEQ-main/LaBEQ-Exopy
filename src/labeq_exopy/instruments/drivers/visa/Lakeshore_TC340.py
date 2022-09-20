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
        print('setting the loop limits')

    def set_heater_range(self,range):
        "Sets Heater Range to 'off' or one of the output values"
        
        self.write('RANGE ' + str(range))
        print('setting heater range')

    def configure_control(self, parameters):
        """CSET configures the control loop parameters of loop 1 or 2:
            control channel, setpoint units, on/off, on/off on startup"""
            
        self.write('CSET ' + str(parameters))
        print('setting the control settings.')
    
    def measure_temperature(self,input):
        """ Returns the temperature reading the selected input in kelvin """
        #note:
        #The RDGST? funciton was used to match the errors displayed on the instrument screen.
        #Using the KRDG? function without RDGST? works just as well.
        #Using RDGST? provides the user with more information than the KRDG? funciton can alone.

        bit_weighting =self.query('RDGST? '+ str(input))
        
        if(float(bit_weighting) == 0):
            K = self.query('KRDG? ' + str(input))
            return float(K)
        elif(float(bit_weighting) == 1):
            return 'Invalid Reading'
        elif(2 <= float(bit_weighting) < 16):
            return 'Old Reading'
        elif( 16 <= float(bit_weighting) < 32):
            return 'T-UNDER'
        elif( 32 <= float(bit_weighting) < 64):
            return 'T-OVER'
        elif( 64 <= float(bit_weighting) < 128):
            return 'S-ZERO'
        elif( 128 <= float(bit_weighting)):
            return 'S-OVER'
        else:
            raise InstrIOError('TC340: Measurement Failed')
    
    def set_PID(self,Auto, pid, loop):
        """ Sets the PID values of the selected loop or sets to AUTO PID"""
        #note: 
        #This was made to chose between full auto or full manual PID.
        #There are other options under the CMODE function which are not included here.
        #(see Lakeshore 340 temperature controller manual)

        if(Auto == True):
            self.write('CMODE ' + str(loop) + ',4')
            print('PID set auto')
        elif (pid != 0):
            self.write('CMODE ' + str(loop) + ',1')
            self.write('PID ' + str(pid))
            print('PID set manual')
        else:
            raise InstrIOError('Auto PID Failed!')
            
    
    def set_mout(self,val):
        """Sets the manual output percentage """
        
        self.write('MOUT ' + str(val))
        print('setting Mout value')
    
    def set_setpoint(self, loop, val):
        """sets the heater setpoint """

        self.write('SETP ' + str(loop) + ',' + str(val))
        print('setting heater setpoint')
    
    def input_settings(self, settings):
        """The INTYPE command controlls all of the input settings for A or B: 
            Diode type, Units, Coefficient, Excitation, Range"""
        #note:
        #The INTYPE options after the 'Diode type' setting are diode specific.
        #They autoset based off the 'Diode type' selection
        #The settings can be manually altered if desired using the next 4 setting options
        #The task file for this driver only prompts the user for the first two inputs

        self.write('INTYPE ' + str(settings))
        print('setting input settings; diode type, units')

    def set_input_curve(self, input, curve):
        """sets the diode curve """
        #note:
        #The curves are diode specific.
        #Correction for this is included in the corresponding task file

        self.write('INCRV ' + str(input) + ',' + str(curve))
        print('setting diode curve')
    
    def TurnLoopOff(self,loop):
        "Turns a loop off"

        self.write('CSET ' + str(loop)+',,,0,0')
        print('turned a loop off')
        

    def set_heater_resistance(self,loop,val):
        """Sets the Heater resistance"""
        #Note:
        #This function works on the assumtion that only one loop is used
        #It can be expanded to use an option for both 1 or 2 loops
        #The function will automatically set the heater output to display in "power" units
        #This can be changed to add the option of "current" units
        #(See Lakeshore TC340 Manual)

        self.write('CDISP ' + str(loop) +',' + '1' + ',' + str(val) + ',2/r/n')
        print('setting heater resistance')
    
    def busy_status(self):
        "returns a 0 if not performing a task and 1 if busy"

        status = self.query('BUSY?')
        print('queried busy status')
        return int(status)

    def TestLoopConfiguration(self,loop):
        #Tests for control configuration initalization
        #If control is not yet configured default settings are selected for the inputted loop
        #Defaults: control loop = A, Units = K, loop = on, powerup enable = on
        #Initalization status is checked through the "powerup enable" setting
        #If the control loop is properly initialized for remote communication, "powerup enable" is set to "on"
        #The "powerup enable" check only works because of how the "configure_control" function input operates
        #In the configure task, "powerup enable" is always turned on if control configurations are inputed
        
        config = self.query('CSET? ' + str(loop))
        print('queried loop configuration')
        
        config = config.split(",")[3]
        
        return int(config)