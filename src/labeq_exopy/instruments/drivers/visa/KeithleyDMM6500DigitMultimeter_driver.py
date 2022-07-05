# -----------------------------------------------------------------------------
# Jake Macdonald, 7/1/2022
# -----------------------------------------------------------------------------
"""Driver for Keithley instruments using VISA library.

"""
from ..driver_tools import (InstrIOError, secure_communication,
                            instrument_property)
from ..visa_tools import VisaInstrument


class Keithley6500(VisaInstrument):

    caching_permissions = {'function': True}

    protocoles = {'TCPIP': 'INSTR'}

    def open_connection(self, **para):
        """Open the connection to the instr using the `connection_str`.

        """
        super(Keithley6500, self).open_connection(**para)
        self.write_termination = '\n'
        self.read_termination = '\n'

    @instrument_property
    @secure_communication()
    def function(self):
        self.read_termination = '\n'

        """Function setter

        """
        value = self.query('FUNCtion?\n')
        if value:
            return value
        else:
            raise InstrIOError('Keithley6500 : Failed to return function')

    @function.setter
    @secure_communication()
    def function(self, value):

        self.write('FUNCtion "{}"'.format(value))
        # The Keithley returns "VOLT:DC" needs to remove the quotes
        if not(self.query('FUNCtion?\n')[1:-1].lower() == value.lower()):
            raise InstrIOError('Keithley6500: Failed to set function')

    @secure_communication()
    def read_voltage_dc(self,mes_range = 'DEF', mes_resolution = 'DEF'):

        """Return the DC voltage read by the instrument.

        Perform a direct reading without any waiting. Can return identical
        values if the instrument is read more often than its integration time.
        The arguments are unused and here only to make this driver and the
        agilent driver compatible.

        """
        
       
        self.write('SENS:FUNC "VOLT:DC"')
        value = self.query('MEAS?')


        #split string into list to get voltage measurement
        value = value.split(",")[0]

        #remove "NVDC" string from measurement so we can cast to a float
        value = value.replace("NVDC","")

        if value:
            return float(value)
        else:
            raise InstrIOError('Keithley6500: DC voltage measure failed')

    @secure_communication()
    def read_voltage_ac(self,mes_range = 'DEF', mes_resolution = 'DEF'):    #need to test if extra parameters are needed
        """Return the AC voltage read by the instrument.

        Perform a direct reading without any waiting. Can return identical
        values if the instrument is read more often than its integration time.
        The arguments are unused and here only to make this driver and the
        agilent driver compatible.

        """

        self.write('SENS:FUNC "VOLT:AC"')
        value = self.query('MEAS?')
        

        #split string into list to get voltage measurement
        value = value.split(",")[0]

        #remove "NVAC" string from measurement so we can cast to a float
        value = value.replace("NVAC","")
        
        if value:
            return float(value)
        else:
            raise InstrIOError('Keithley6500: AC voltage measure failed')

    @secure_communication()
    def read_two_resistance(self):
        """
        Return the two wire resistance read by the instrument.

        Perform a direct reading without any waiting. Can return identical
        values if the instrument is read more often than its integration time.
        The arguments are unused and here only to make this driver and the
        agilent driver compatible.

        """
        self.write('SENS:FUNC "res"')




        value = self.query('MEAS?')

        #split string into list to get current measurement
        value = value.split(",")[0]

        #remove "NOHM" string from measurement so we can cast to a float
        value = value.replace("NOHM","")
        
        if value:
            return float(value)
        else:
            raise InstrIOError('Keithley6500: Resistance measure failed')

    @secure_communication()
    def read_four_resistance(self):
        """
        Return the four wire resistance read by the instrument.

        Perform a direct reading without any waiting. Can return identical
        values if the instrument is read more often than its integration time.
        The arguments are unused and here only to make this driver and the
        agilent driver compatible.

        """
        self.write('SENS:FUNC "fres"')


        value = self.query('MEAS?')

        #split string into list to get current measurement
        value = value.split(",")[0]

        #remove "NOHM4W" string from measurement so we can cast to a float
        value = value.replace("NOHM4W","")
        
        if value:
            return float(value)
        else:
            raise InstrIOError('Keithley6500: Four Wire Resistance measure failed')

    @secure_communication()
    def read_current_dc(self,mes_range = 'DEF', mes_resolution = 'DEF'):
        """Return the DC current read by the instrument.

        Perform a direct reading without any waiting. Can return identical
        values if the instrument is read more often than its integration time.
        The arguments are unused and here only to make this driver and the
        agilent driver compatible.

        """
        self.write('SENS:FUNC "CURR:DC"')


        #query device with meas? command returning comma seperated string with measurement value, timestamp, reading count
        # and channel
        value = self.query('meas?')

        #split string into list to get current measurement
        value = value.split(",")[0]

        #remove "NADC" string from measurement so we can cast to a float
        value = value.replace("NADC","")

        if value:
            return float(value)
        else:
            raise InstrIOError('Keithley6500: DC current measure failed')

    @secure_communication()
    def read_current_ac(self,mes_range = 'DEF', mes_resolution = 'DEF'):
        """Return the AC current read by the instrument.

        Perform a direct reading without any waiting. Can return identical
        values if the instrument is read more often than its integration time.
        The arguments are unused and here only to make this driver and the
        agilent driver compatible.

        """
        self.write('SENS:FUNC "VOLT:DC"')
        value = self.query('MEAS?')
        
        #split string into list to get current measurement
        value = value.split(",")[0]

        #remove "NAAC" string from measurement so we can cast to a float
        value = value.replace("NAAC","")
        if value:
            return float(value)
        else:
            raise InstrIOError('Keithley6500: AC current measure failed')

    @secure_communication()
    def check_connection(self):
        """Check wether or not a front panel user set the instrument in local.

        If a front panel user set the instrument in local the cache can be
        corrupted and should be cleared.

        """
        val = ('{0:08b}'.format(int(self.query('*ESR'))))[::-1]
        if val:
            return val[6]

