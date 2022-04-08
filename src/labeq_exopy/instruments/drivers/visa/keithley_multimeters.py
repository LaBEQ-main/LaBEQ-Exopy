# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyHqcLegacy Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Driver for Keithley instruments using VISA library.

"""
from ..driver_tools import (InstrIOError, secure_communication,
                            instrument_property)
from ..visa_tools import VisaInstrument


class Keithley2000(VisaInstrument):
    """Driver for Keithley 2000 using the VISA library

    This driver does not give access to all the functionnality of the
    instrument but you can extend it if needed. See the documentation of the
    driver_tools package for more details about writing instruments drivers.

    Parameters
    ----------
    see the `VisaInstrument` parameters

    Attributes
    ----------
    function : str, instrument_property
        Current function of the multimeter. Can be : 'VOLT:DC', 'VOLT:AC',
        'CURR:DC', 'CURR:AC', 'RES'. This instrument property is cached by
        default.

    Methods
    -------
    read_voltage_dc(mes_range = 'DEF', mes_resolution = 'DEF')
        Return the DC voltage read by the instrument. Can change the function
        if needed.
    read_voltage_ac(mes_range = 'DEF', mes_resolution = 'DEF')
        Return the AC voltage read by the instrument. Can change the function
        if needed.
    read_res(mes_range = 'DEF', mes_resolution = 'DEF')
        Return the resistance read by the instrument. Can change the function
        if needed.
    read_current_dc(mes_range = 'DEF', mes_resolution = 'DEF')
        Return the DC current read by the instrument. Can change the function
        if needed.
    read_current_ac(mes_range = 'DEF', mes_resolution = 'DEF')
        Return the AC current read by the instrument. Can change the function
        if needed.

    """
    caching_permissions = {'function': True}

    protocoles = {'GPIB': 'INSTR'}

    def open_connection(self, **para):
        """Open the connection to the instr using the `connection_str`.

        """
        super(Keithley2000, self).open_connection(**para)
        self.write_termination = '\n'
        self.read_termination = '\n'

    @instrument_property
    @secure_communication()
    def function(self):
        """Function setter

        """
        value = self.query('FUNCtion?')
        if value:
            return value
        else:
            raise InstrIOError('Keithley2000 : Failed to return function')

    @function.setter
    @secure_communication()
    def function(self, value):
        self.write('FUNCtion "{}"'.format(value))
        # The Keithley returns "VOLT:DC" needs to remove the quotes
        if not(self.query('FUNCtion?')[1:-1].lower() == value.lower()):
            raise InstrIOError('Keithley2000: Failed to set function')

    @secure_communication()
    def read_voltage_dc(self, mes_range='DEF', mes_resolution='DEF'):
        """Return the DC voltage read by the instrument.

        Perform a direct reading without any waiting. Can return identical
        values if the instrument is read more often than its integration time.
        The arguments are unused and here only to make this driver and the
        agilent driver compatible.

        """
        if self.function != 'VOLT:DC':
            self.function = 'VOLT:DC'

        value = self.query('FETCh?')
        if value:
            return float(value)
        else:
            raise InstrIOError('Keithley2000: DC voltage measure failed')

    @secure_communication()
    def read_voltage_ac(self, mes_range='DEF', mes_resolution='DEF'):
        """Return the AC voltage read by the instrument.

        Perform a direct reading without any waiting. Can return identical
        values if the instrument is read more often than its integration time.
        The arguments are unused and here only to make this driver and the
        agilent driver compatible.

        """
        if self.function != 'VOLT:AC':
            self.function = 'VOLT:AC'

        value = self.query('FETCh?')
        if value:
            return float(value)
        else:
            raise InstrIOError('Keithley2000: AC voltage measure failed')

    @secure_communication()
    def read_resistance(self, mes_range='DEF', mes_resolution='DEF'):
        """
        Return the resistance read by the instrument.

        Perform a direct reading without any waiting. Can return identical
        values if the instrument is read more often than its integration time.
        The arguments are unused and here only to make this driver and the
        agilent driver compatible.

        """
        if self.function != 'RES':
            self.function = 'RES'

        value = self.query('FETCh?')
        if value:
            return float(value)
        else:
            raise InstrIOError('Keithley2000: Resistance measure failed')

    @secure_communication()
    def read_current_dc(self, mes_range='DEF', mes_resolution='DEF'):
        """Return the DC current read by the instrument.

        Perform a direct reading without any waiting. Can return identical
        values if the instrument is read more often than its integration time.
        The arguments are unused and here only to make this driver and the
        agilent driver compatible.

        """
        if self.function != 'CURR:DC':
            self.function = 'CURR:DC'

        value = self.query('FETCh?')
        if value:
            return float(value)
        else:
            raise InstrIOError('Keithley2000: DC current measure failed')

    @secure_communication()
    def read_current_ac(self, mes_range='DEF', mes_resolution='DEF'):
        """Return the AC current read by the instrument.

        Perform a direct reading without any waiting. Can return identical
        values if the instrument is read more often than its integration time.
        The arguments are unused and here only to make this driver and the
        agilent driver compatible.

        """
        if self.function != 'CURR:AC':
            self.function = 'CURR:AC'

        value = self.query('FETCh?')
        if value:
            return float(value)
        else:
            raise InstrIOError('Keithley2000: AC current measure failed')

    @secure_communication()
    def check_connection(self):
        """Check wether or not a front panel user set the instrument in local.

        If a front panel user set the instrument in local the cache can be
        corrupted and should be cleared.

        """
        val = ('{0:08b}'.format(int(self.query('*ESR'))))[::-1]
        if val:
            return val[6]

class Keithley2001(VisaInstrument):
    """Driver for Keithley 2000 using the VISA library

    This driver does not give access to all the functionnality of the
    instrument but you can extend it if needed. See the documentation of the
    driver_tools package for more details about writing instruments drivers.

    Parameters
    ----------
    see the `VisaInstrument` parameters

    Attributes
    ----------
    function : str, instrument_property
        Current function of the multimeter. Can be : 'VOLT:DC', 'VOLT:AC',
        'CURR:DC', 'CURR:AC', 'RES'. This instrument property is cached by
        default.

    Methods
    -------
    read_voltage_dc(mes_range = 'DEF', mes_resolution = 'DEF')
        Return the DC voltage read by the instrument. Can change the function
        if needed.
    read_voltage_ac(mes_range = 'DEF', mes_resolution = 'DEF')
        Return the AC voltage read by the instrument. Can change the function
        if needed.
    read_res(mes_range = 'DEF', mes_resolution = 'DEF')
        Return the resistance read by the instrument. Can change the function
        if needed.
    read_current_dc(mes_range = 'DEF', mes_resolution = 'DEF')
        Return the DC current read by the instrument. Can change the function
        if needed.
    read_current_ac(mes_range = 'DEF', mes_resolution = 'DEF')
        Return the AC current read by the instrument. Can change the function
        if needed.

    """
    caching_permissions = {'function': True}

    protocoles = {'GPIB': 'INSTR'}

    def open_connection(self, **para):
        """Open the connection to the instr using the `connection_str`.

        """
        super(Keithley2001, self).open_connection(**para)
        self.write_termination = '\n'
        self.read_termination = '\n'

    @instrument_property
    @secure_communication()
    def function(self):
        """Function setter

        """
        value = self.query('FUNCtion?')
        if value:
            return value
        else:
            raise InstrIOError('Keithley2000 : Failed to return function')

    @function.setter
    @secure_communication()
    def function(self, value):
        self.write('FUNCtion "{}"'.format(value))
        # The Keithley returns "VOLT:DC" needs to remove the quotes
        if not(self.query('FUNCtion?')[1:-1].lower() == value.lower()):
            raise InstrIOError('Keithley2001: Failed to set function')

    @secure_communication()
    def read_voltage_dc(self, mes_range='DEF', mes_resolution='DEF'):
        """Return the DC voltage read by the instrument.

        Perform a direct reading without any waiting. Can return identical
        values if the instrument is read more often than its integration time.
        The arguments are unused and here only to make this driver and the
        agilent driver compatible.

        """
        if self.function != 'VOLT:DC':
            self.function = 'VOLT:DC'

        value = self.query('MEAS?')

        #split string into list to get voltage measurement
        value = value.split(",")[0]

        #remove "NVDC" string from measurement so we can cast to a float
        value = value.replace("NVDC","")

        if value:
            return float(value)
        else:
            raise InstrIOError('Keithley2001: DC voltage measure failed')

    @secure_communication()
    def read_voltage_ac(self, mes_range='DEF', mes_resolution='DEF'):
        """Return the AC voltage read by the instrument.

        Perform a direct reading without any waiting. Can return identical
        values if the instrument is read more often than its integration time.
        The arguments are unused and here only to make this driver and the
        agilent driver compatible.

        """
        if self.function != 'VOLT:AC':
            self.function = 'VOLT:AC'

        value = self.query('MEAS?')

        #split string into list to get voltage measurement
        value = value.split(",")[0]

        #remove "NVAC" string from measurement so we can cast to a float
        value = value.replace("NVAC","")
        
        if value:
            return float(value)
        else:
            raise InstrIOError('Keithley2001: AC voltage measure failed')

    @secure_communication()
    def read_two_resistance(self, mes_range='DEF', mes_resolution='DEF'):
        """
        Return the two wire resistance read by the instrument.

        Perform a direct reading without any waiting. Can return identical
        values if the instrument is read more often than its integration time.
        The arguments are unused and here only to make this driver and the
        agilent driver compatible.

        """
        if self.function != 'RES':
            self.function = 'RES'

        value = self.query('MEAS?')

        #split string into list to get current measurement
        value = value.split(",")[0]

        #remove "NOHM" string from measurement so we can cast to a float
        value = value.replace("NOHM","")
        
        if value:
            return float(value)
        else:
            raise InstrIOError('Keithley2001: Resistance measure failed')

    @secure_communication()
    def read_four_resistance(self, mes_range='DEF', mes_resolution='DEF'):
        """
        Return the four wire resistance read by the instrument.

        Perform a direct reading without any waiting. Can return identical
        values if the instrument is read more often than its integration time.
        The arguments are unused and here only to make this driver and the
        agilent driver compatible.

        """
        if self.function != 'FRES':
            self.function = 'FRES'

        value = self.query('MEAS?')

        #split string into list to get current measurement
        value = value.split(",")[0]

        #remove "NOHM4W" string from measurement so we can cast to a float
        value = value.replace("NOHM4W","")
        
        if value:
            return float(value)
        else:
            raise InstrIOError('Keithley2001: Four Wire Resistance measure failed')

    @secure_communication()
    def read_current_dc(self, mes_range='DEF', mes_resolution='DEF'):
        """Return the DC current read by the instrument.

        Perform a direct reading without any waiting. Can return identical
        values if the instrument is read more often than its integration time.
        The arguments are unused and here only to make this driver and the
        agilent driver compatible.

        """
        if self.function != 'CURR:DC':
            self.function = 'CURR:DC'

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
            raise InstrIOError('Keithley2001: DC current measure failed')

    @secure_communication()
    def read_current_ac(self, mes_range='DEF', mes_resolution='DEF'):
        """Return the AC current read by the instrument.

        Perform a direct reading without any waiting. Can return identical
        values if the instrument is read more often than its integration time.
        The arguments are unused and here only to make this driver and the
        agilent driver compatible.

        """
        if self.function != 'CURR:AC':
            self.function = 'CURR:AC'

        value = self.query('MEAS?')
        
        #split string into list to get current measurement
        value = value.split(",")[0]

        #remove "NAAC" string from measurement so we can cast to a float
        value = value.replace("NAAC","")
        if value:
            return float(value)
        else:
            raise InstrIOError('Keithley2001: AC current measure failed')

    @secure_communication()
    def check_connection(self):
        """Check wether or not a front panel user set the instrument in local.

        If a front panel user set the instrument in local the cache can be
        corrupted and should be cleared.

        """
        val = ('{0:08b}'.format(int(self.query('*ESR'))))[::-1]
        if val:
            return val[6]

class Keithley2400(VisaInstrument):
    """Driver for Keithley 2000 using the VISA library

    This driver does not give access to all the functionnality of the
    instrument but you can extend it if needed. See the documentation of the
    driver_tools package for more details about writing instruments drivers.

    Parameters
    ----------
    see the `VisaInstrument` parameters

    Attributes
    ----------
    function : str, instrument_property
        Current function of the multimeter. Can be : 'VOLT:DC', 'VOLT:AC',
        'CURR:DC', 'CURR:AC', 'RES'. This instrument property is cached by
        default.

    Methods
    -------
    read_voltage_dc(mes_range = 'DEF', mes_resolution = 'DEF')
        Return the DC voltage read by the instrument. Can change the function
        if needed.
    read_voltage_ac(mes_range = 'DEF', mes_resolution = 'DEF')
        Return the AC voltage read by the instrument. Can change the function
        if needed.
    read_res(mes_range = 'DEF', mes_resolution = 'DEF')
        Return the resistance read by the instrument. Can change the function
        if needed.
    read_current_dc(mes_range = 'DEF', mes_resolution = 'DEF')
        Return the DC current read by the instrument. Can change the function
        if needed.
    read_current_ac(mes_range = 'DEF', mes_resolution = 'DEF')
        Return the AC current read by the instrument. Can change the function
        if needed.

    """
    caching_permissions = {'function': True}

    protocoles = {'GPIB': 'INSTR'}

    def open_connection(self, **para):
        """Open the connection to the instr using the `connection_str`.

        """
        super(Keithley2400, self).open_connection(**para)
        self.write_termination = '\n'
        self.read_termination = '\n'

    @instrument_property
    @secure_communication()
    def function(self):
        """Function setter

        """
        value = self.query('FUNCtion?')
        if value:
            return value
        else:
            raise InstrIOError('Keithley2000 : Failed to return function')

    @function.setter
    @secure_communication()
    def function(self, value):
        self.write('FUNCtion "{}"'.format(value))
        # The Keithley returns "VOLT:DC" needs to remove the quotes
        if not(self.query('FUNCtion?')[1:-1].lower() == value.lower()):
            raise InstrIOError('Keithley2000: Failed to set function')

    @secure_communication()
    def read_voltage_dc(self, mes_range='DEF', mes_resolution='DEF'):
        """Return the DC voltage read by the instrument.

        Perform a direct reading without any waiting. Can return identical
        values if the instrument is read more often than its integration time.
        The arguments are unused and here only to make this driver and the
        agilent driver compatible.

        """
        if self.function != 'VOLT:DC':
            self.function = 'VOLT:DC'

        value = self.query('FETCh?')
        if value:
            return float(value)
        else:
            raise InstrIOError('Keithley2000: DC voltage measure failed')

    @secure_communication()
    def read_voltage_ac(self, mes_range='DEF', mes_resolution='DEF'):
        """Return the AC voltage read by the instrument.

        Perform a direct reading without any waiting. Can return identical
        values if the instrument is read more often than its integration time.
        The arguments are unused and here only to make this driver and the
        agilent driver compatible.

        """
        if self.function != 'VOLT:AC':
            self.function = 'VOLT:AC'

        value = self.query('FETCh?')
        if value:
            return float(value)
        else:
            raise InstrIOError('Keithley2000: AC voltage measure failed')

    @secure_communication()
    def read_resistance(self, mes_range='DEF', mes_resolution='DEF'):
        """
        Return the resistance read by the instrument.

        Perform a direct reading without any waiting. Can return identical
        values if the instrument is read more often than its integration time.
        The arguments are unused and here only to make this driver and the
        agilent driver compatible.

        """
        if self.function != 'RES':
            self.function = 'RES'

        value = self.query('FETCh?')
        if value:
            return float(value)
        else:
            raise InstrIOError('Keithley2000: Resistance measure failed')

    @secure_communication()
    def read_current_dc(self, mes_range='DEF', mes_resolution='DEF'):
        """Return the DC current read by the instrument.

        Perform a direct reading without any waiting. Can return identical
        values if the instrument is read more often than its integration time.
        The arguments are unused and here only to make this driver and the
        agilent driver compatible.

        """
        if self.function != 'CURR:DC':
            self.function = 'CURR:DC'

        value = self.query('FETCh?')
        if value:
            return float(value)
        else:
            raise InstrIOError('Keithley2000: DC current measure failed')

    @secure_communication()
    def read_current_ac(self, mes_range='DEF', mes_resolution='DEF'):
        """Return the AC current read by the instrument.

        Perform a direct reading without any waiting. Can return identical
        values if the instrument is read more often than its integration time.
        The arguments are unused and here only to make this driver and the
        agilent driver compatible.

        """
        if self.function != 'CURR:AC':
            self.function = 'CURR:AC'

        value = self.query('FETCh?')
        if value:
            return float(value)
        else:
            raise InstrIOError('Keithley2000: AC current measure failed')

    @secure_communication()
    def check_connection(self):
        """Check wether or not a front panel user set the instrument in local.

        If a front panel user set the instrument in local the cache can be
        corrupted and should be cleared.

        """
        val = ('{0:08b}'.format(int(self.query('*ESR'))))[::-1]
        if val:
            return val[6]
