# -----------------------------------------------------------------------------
# Jake Macdonald, 7/1/2022
# -----------------------------------------------------------------------------
"""Driver for Keithley instruments using VISA library.

"""
from ..driver_tools import (InstrIOError, secure_communication,
                            instrument_property)
from ..visa_tools import VisaInstrument


class GWINSTEK1054B(VisaInstrument):

    caching_permissions = {'function': True}

    protocoles = {'TCPIP': 'INSTR'}

    def open_connection(self, **para):
        """Open the connection to the instr using the `connection_str`.

        """
        super(GWINSTEK1054B, self).open_connection(**para)
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

    @secure_communication()
    def check_connection(self):
        """Check wether or not a front panel user set the instrument in local.

        If a front panel user set the instrument in local the cache can be
        corrupted and should be cleared.

        """
        val = ('{0:08b}'.format(int(self.query('*ESR'))))[::-1]
        if val:
            return val[6]


    @secure_communication()
    def read_mean(self):       
        value = self.query('MEAS:mean?')
        print(self.query('func?'))

        if value:
            return float(value)
        else:
            raise InstrIOError('Keithley6500: DC voltage measure failed')
    
  
   