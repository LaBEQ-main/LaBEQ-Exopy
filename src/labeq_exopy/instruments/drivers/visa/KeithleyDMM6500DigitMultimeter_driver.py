# -----------------------------------------------------------------------------
# Jake Macdonald, 7/1/2022
# -----------------------------------------------------------------------------
"""Driver for Keithley instruments using VISA library.

"""
from ..driver_tools import (InstrIOError, secure_communication,
                            instrument_property)
from ..visa_tools import VisaInstrument
from time import sleep



class Keithley6500(VisaInstrument):
    rangeVal = ""


    caching_permissions = {'function': True}

    protocoles = {'TCPIP': 'INSTR'}

    def open_connection(self, **para):
        """Open the connection to the instr using the `connection_str`.

        """
        super(Keithley6500, self).open_connection(**para)
        self.write_termination = '\n'
        self.read_termination = '\n'

    @secure_communication()
    def read_voltage_dc(self):
    # The SENS:FUNC setting may be circumvented by using MEAS:FUNC ('SENS:FUNC "VOLT:DC"')
    #MEAS:FUNC is a coupling of the sens:func and data?

        self.query('MEAS:VOLT:DC?')
        value = self.query('read?')

        # print ("DC VOLT " + value)
        value = value.split(",")[0]

        #remove "NVDC" string from measurement so we can cast to a float
        value = value.replace("NVDC","")

        if value:
            return float(value)
        else:
            raise InstrIOError('Keithley6500: DC voltage measure failed')

    @secure_communication()
    def read_voltage_ac(self):    


                

        self.query('MEAS:VOLT:AC?')
        value = self.query('read?')

        # print ("AC VOLT " + value)


        value = value.split(",")[0]
        value = value.replace("NVAC","")
        
        if value:
            return float(value)
        else:
            raise InstrIOError('Keithley6500: AC voltage measure failed')

    @secure_communication()
    def read_two_resistance(self):

        
        self.query('MEAS:RES?')
        value = self.query('read?')

        # print ("RES " + value)

        value = value.split(",")[0]
        value = value.replace("NOHM","")
        
        if value:
            return float(value)
        else:
            raise InstrIOError('Keithley6500: Resistance measure failed')

    @secure_communication()
    def read_four_resistance(self):
        self.query('MEAS:FRES?')
        value = self.query('read?')

        # print ("FRES " + value)


        value = value.split(",")[0]
        value = value.replace("NOHM4W","")
        
        if value:
            return float(value)
        else:
            raise InstrIOError('Keithley6500: Four Wire Resistance measure failed')

    @secure_communication()
    def read_current_dc(self):
        
        self.query('MEAS:CURR:DC?')
        value = self.query('read?')

        # print ("DC CURR " + value)

        value = value.split(",")[0]
        value = value.replace("NADC","")

        if value:
            return float(value)
        else:
            raise InstrIOError('Keithley6500: DC current measure failed')

    @secure_communication()
    def read_current_ac(self):
        
        self.query('MEAS:CURR:AC?')
        value = self.query('read?')

        # print ("AC CURR " + value)


        value = value.split(",")[0]
        value = value.replace("NAAC","")

        if value:
            return float(value)
        else:
            raise InstrIOError('Keithley6500: AC current measure failed')

    @secure_communication()
    def set_range(self, range_val):
        if not range_val :
            self.write('SENS:VOLT:RANG 100')
            self.rangeVal = ""
        else:
            self.rangeVal = str(range_val)

    @secure_communication()
    def check_connection(self):
        """Check wether or not a front panel user set the instrument in local.

        If a front panel user set the instrument in local the cache can be
        corrupted and should be cleared.

        """
        val = ('{0:08b}'.format(int(self.query('*ESR'))))[::-1]
        if val:
            return val[6]

