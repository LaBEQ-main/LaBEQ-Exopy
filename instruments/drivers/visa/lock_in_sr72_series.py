# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyHqcLegacy Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Drivers for lock-in from Signal Recovery using VISA library.

"""
from ..driver_tools import (InstrIOError, secure_communication)
from ..visa_tools import VisaInstrument


class LockInSR7265(VisaInstrument):
    """Driver for a SR7265 lock-in, using the VISA library.

    This driver does not give access to all the functionnality of the
    instrument but you can extend it if needed. See the documentation of the
    driver_tools package for more details about writing instruments drivers.

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

    Notes
    -----
    The completion of each command is checked by reading the status byte (see
    `_check_completion` method)

    """
    def open_connection(self, **para):
        """Open the connection to the instr using the `connection_str`.

        """
        super(LockInSR7265, self).open_connection(**para)
        self.write_termination = '\n'
        self.read_termination = '\n'

    @secure_communication()
    def read_x(self):
        """
        Return the x quadrature measured by the instrument

        Perform a direct reading without any waiting. Can return non
        independent values if the instrument is queried too often.

        """
        value = self.query('X.')
        status = self._check_status()
        if status != 'OK' or not value:
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
        value = self.query('Y.')
        status = self._check_status()
        if status != 'OK' or not value:
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
        values = self.query_ascii_values('XY.')
        status = self._check_status()
        if status != 'OK' or not values:
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
        value = self.query('MAG.')
        status = self._check_status()
        if status != 'OK' or not value:
            return InstrIOError('The command did not complete correctly')
        else:
            return float(value)

    @secure_communication()
    def read_phase(self):
        """
        Return the phase of the signal measured by the instrument

        Perform a direct reading without any waiting. Can return non
        independent values if the instrument is queried too often.

        """
        value = self.query('PHA.')
        status = self._check_status()
        if status != 'OK' or not value:
            raise InstrIOError('The command did not complete correctly')
        else:
            return float(value)

    @secure_communication()
    def read_amp_and_phase(self):
        """
        Return the amplitude and phase of the signal measured by the instrument

        Perform a direct reading without any waiting. Can return non
        independent values if the instrument is queried too often.

        """
        values = self.query_ascii_values('MP.')
        status = self._check_status()
        if status != 'OK' or not values:
            raise InstrIOError('The command did not complete correctly')
        else:
            return values

    @secure_communication()
    def _check_status(self):
        """
        Read the value of the status byte to determine if the last command
        executed properly
        """
        bites = self.query('ST')
        status_byte = ('{0:08b}'.format(ord(bites[0])))[::-1]
        if not status_byte[0]:
            return 'Command went wrong'
        else:
            return 'OK'


class LockInSR7270(LockInSR7265):
    """
    Driver for a SR7270 lock-in, using the VISA library.

    This driver does not give access to all the functionnality of the
    instrument but you can extend it if needed. See the documentation of the
    driver_tools package for more details about writing instruments drivers.

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

    Notes
    -----
    The completion of each command is checked by reading the status byte (see
    `_check_completion` method).
    The only difference between this driver and the one for the SR7265 is the
    termination character used and the fact that the SR7270 automatically
    return the status byte.

    """

    def __init__(self, *args, **kwargs):

        super(LockInSR7270, self).__init__(*args, **kwargs)
        self.write_termination = '\0'
        self.read_termination = '\0'

    @secure_communication()
    def _check_status(self):
        """
        Read the value of the status byte to determine if the last command
        executed properly
        """
        bites = self.read()
        status_byte = ('{0:08b}'.format(ord(bites[0])))[::-1]
        if not status_byte[0]:
            return 'Command went wrong'
        else:
            return 'OK'
