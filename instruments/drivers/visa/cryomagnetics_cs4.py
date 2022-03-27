# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyHqcLegacy Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Driver for the Cryomagnetic superconducting magnet power supply CS4.

"""
from inspect import cleandoc
from time import sleep

from ..driver_tools import (InstrIOError, secure_communication,
                            instrument_property, InstrJob)
from ..visa_tools import VisaInstrument


_GET_HEATER_DICT = {'0': 'Off',
                    '1': 'On'}

_ACTIVITY_DICT = {'To set point': 'UP',
                  'Hold': 'PAUSE'}


class CS4(VisaInstrument):
    """Driver for the superconducting magnet power supply Cryomagnetics CS4.

    """

    #: Typical fluctuations at the output of the instrument.
    #: We use a class variable since we expect this to be identical for all
    #: instruments.
    OUTPUT_FLUCTUATIONS = 2e-4

    caching_permissions = {'heater_state': True,
                           'target_field': True,
                           'sweep_rate_field': True,
                           }

    def __init__(self, connection_info, caching_allowed=True,
                 caching_permissions={}, auto_open=True):
        super().__init__(connection_info, caching_allowed,
                                  caching_permissions)
        try:
            mc = connection_info['magnet_conversion']
            self.field_current_ratio = float(mc)
        except KeyError:
            raise InstrIOError(cleandoc('''The field to current ratio
                 of the currently used magnet need to be specified in
                 the instrument settings. One should also check that
                 the switch heater current is correct.'''))

        if 'output_fluctuations' in connection_info:
            self.output_fluctuations = connection_info['output_fluctuations']
        else:
            self.output_fluctuations = self.OUTPUT_FLUCTUATIONS

    def open_connection(self, **para):
        """Open the connection and set up the parameters.

        """
        super(CS4, self).open_connection(**para)
        if not para:
            self.write_termination = '\n'
            self.read_termination = '\n'

        # Setup the correct unit and range.
        self.write('UNITS T')
        self.write('RANGE 0 100;')  # HINT the CG4 requires the ;
        # we'll only use the command sweep up (ie to upper limit)
        # however upper limit can't be lower than lower limit for
        # some sources : G4 for example
        # set lower limit to lowest value
        self.write('LLIM -7')

    @secure_communication()
    def read_output_field(self):
        """Read the current value of the output field.

        """
        return float(self.query('IOUT?').strip(' T'))

    @secure_communication()
    def read_persistent_field(self):
        """Read the current value of the persistent field.

        """
        return float(self.query('IMAG?').strip(' T'))

    def is_target_reached(self):
        """Check whether the target field has been reached.

        """
        return (abs(self.read_output_field() - self.target_field) <
                self.output_fluctuations)

    def sweep_to_persistent_field(self):
        """Convenience function ramping the field to the persistent.

        Once the value is reached one can safely turn on the switch heater.

        """
        return self.sweep_to_field(self.read_persistent_field())

    def sweep_to_field(self, value, rate=None):
        """Convenience function to ramp up the field to the specified value.

        """
        # Set rate. Always the fast sweep rate if the switch heater is off.
        if rate is not None:
            self.field_sweep_rate = rate
        rate = (self.field_sweep_rate if self.heater_state == 'On' else
                self.fast_sweep_rate)

        # Start ramping.
        self.target_field = value
        self.activity = 'To set point'

        # Create job.
        span = abs(self.read_output_field() - value)
        wait = 60 * span / rate
        job = InstrJob(self.is_target_reached, wait, cancel=self.stop_sweep)
        return job

    def stop_sweep(self):
        """Stop the field sweep at the current value.

        """
        self.activity = 'Hold'

    def check_connection(self):
        pass

    @instrument_property
    @secure_communication()
    def heater_state(self):
        """State of the switch heater allowing to inject current into the
        coil.

        """
        heat = self.query('PSHTR?').strip()
        try:
            return _GET_HEATER_DICT[heat]
        except KeyError:
            raise ValueError('The switch is in fault or absent')

    @heater_state.setter
    @secure_communication()
    def heater_state(self, state):
        if state in ['On', 'Off']:
            self.write('PSHTR {}'.format(state))
            sleep(1)

    @instrument_property
    @secure_communication()
    def field_sweep_rate(self):
        """Rate at which to ramp the field (T/min).

        """
        # converted from A/s to T/min
        rate = float(self.query('RATE? 0'))
        return rate * (60 * self.field_current_ratio)

    @field_sweep_rate.setter
    @secure_communication()
    def field_sweep_rate(self, rate):
        # converted from T/min to A/s
        rate /= 60 * self.field_current_ratio
        self.write('RATE 0 {}'.format(rate))

    @instrument_property
    @secure_communication()
    def fast_sweep_rate(self):
        """Rate at which to ramp the field when the switch heater is off
        (T/min).

        """
        rate = float(self.query('RATE? 3'))
        return rate * (60 * self.field_current_ratio)

    @fast_sweep_rate.setter
    @secure_communication()
    def fast_sweep_rate(self, rate):
        rate /= 60 * self.field_current_ratio
        self.write('RATE 3 {}'.format(rate))

    @instrument_property
    @secure_communication()
    def target_field(self):
        """Field that the source will try to reach.

        """
        # in T
        return float(self.query('ULIM?').strip(' T'))

    @target_field.setter
    @secure_communication()
    def target_field(self, target):
        """Sweep the output intensity to reach the specified ULIM (in T)
        at a rate depending on the intensity, as defined in the range(s).

        """
        self.write('ULIM {}'.format(target))

    @instrument_property
    @secure_communication()
    def persistent_field(self):
        """Last known value of the magnet field.

        """
        return float(self.query('IMAG?').strip(' T'))

    @instrument_property
    @secure_communication()
    def activity(self):
        """Current activity of the power supply (idle, ramping).

        """
        return self.query('SWEEP?').strip()

    @activity.setter
    @secure_communication()
    def activity(self, value):
        par = _ACTIVITY_DICT.get(value, None)
        if par != 'PAUSE':
            if self.heater_state == 'Off':
                par += ' FAST'
            else:
                par += ' SLOW'
        if par:
            self.write('SWEEP ' + par)
        else:
            raise ValueError(cleandoc(''' Invalid parameter {} sent to
                             CS4 set_activity method'''.format(value)))
