# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyHqcLegacy Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Drivers for oxford ips magnet supply using VISA library.

"""
from inspect import cleandoc
from time import sleep
from ..driver_tools import (InstrIOError, secure_communication,
                            instrument_property, InstrJob)
from ..visa_tools import VisaInstrument

_PARAMETER_DICT = {'Demand current': 0,
                   'Supply voltage': 1,
                   'Magnet current': 2,
                   'Target current': 5,
                   'Current sweep rate': 6,
                   'Demand field': 7,  # This is the output field !!!
                   'Target field': 8,
                   'Field sweep rate': 9,
                   'Software voltage limit': 15,
                   'Persistent magnet current': 16,
                   'Trip current': 17,
                   'Persistent magnet field': 18,
                   'Trip field': 19,
                   'Switch heater current': 20,
                   'Positive current limit': 21,
                   'Negative current limit': 22,
                   'Lead resistance': 23,
                   'Magnet inductance': 24}

_ACTIVITY_DICT = {'Hold': 0,
                  'To set point': 1,
                  'To zero': 2,
                  'Clamp': 4}

_CONTROL_DICT = {'Local & Locked': 0,
                 'Remote & Locked': 1,
                 'Local & Unlocked': 2,
                 'Remote & Unlocked': 3}

_GET_HEATER_DICT = {0: 'Off Magnet at Zero',
                    1: 'On (switch open)',
                    2: 'Off Magnet at Field',
                    5: 'Heater Fault',
                    8: 'No Switch Fitted'}


class IPS12010(VisaInstrument):
    """Driver for the superconducting magnet power supply IPS120-10

    """

    #: Typical fluctuations at the ouput of the instrument.
    #: We use a class variable since we expect this to be identical for all
    #: instruments.
    OUTPUT_FLUCTUATIONS = 2e-4

    caching_permissions = {'heater_state': True,
                           'target_current': True,
                           'sweep_rate_current': True,
                           'target_field': True,
                           'sweep_rate_field': True,
                           }

    def __init__(self, connection_info, caching_allowed=True,
                 caching_permissions={}):
        super(IPS12010, self).__init__(connection_info, caching_allowed,
                                       caching_permissions)
        self.write_termination = '\r'
        self.read_termination = '\r'

        if 'output_fluctuations' in connection_info:
            self.output_fluctuations = connection_info['output_fluctuations']
        else:
            self.output_fluctuations = self.OUTPUT_FLUCTUATIONS

    def open_connection(self, **para):
        """Open the connection and set up the parameters.

        """
        super(IPS12010, self).open_connection(**para)
        self.control = 'Remote & Unlocked'
        self.set_communications_protocol(False, True)
        self.set_mode('TESLA')

    def read_persistent_current(self):
        """Read the current value of the persistent current.

        """
        return float(self.read_parameter('Persistent magnet current'))

    def read_persistent_field(self):
        """Read the current value of the persistent field.

        """
        return float(self.read_parameter('Persistent magnet field'))

    def read_output_field(self):
        """Read the current value output field.

        """
        return float(self.read_parameter('Demand field'))

    def is_target_reached(self):
        """Check whether the target field has been reached.

        """
        status = self._get_status()
        output = int(status[11])
        if not output:
            return (abs(self.read_output_field() - self.target_field) <
                    self.output_fluctuations)
        else:
            return False

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

    def get_full_heater_state(self):
        """Get the complete status of the switch heater, including faults.

        """
        status = self._get_status()
        heat = int(status[8])
        return _GET_HEATER_DICT[heat]

    @secure_communication()
    def set_mode(self, mode):
        """Set the working mode of the source.

        This determines whether the source uses T or A.

        """
        if mode == 'AMPS':
            result = self.query('M8')
            if result.startswith('?'):
                raise InstrIOError(cleandoc('''IPS120-10 did not set the
                    heater mode to {}'''.format(mode)))
        elif mode == 'TESLA':
            result = self.query('M9')
            if result.startswith('?'):
                raise InstrIOError(cleandoc('''IPS120-10 did not set the
                    heater mode to {}'''.format(mode)))
        else:
            raise ValueError(cleandoc(''' Invalid parameter {} sent to
                IPS120-10 set_mode method'''.format(mode)))

    @secure_communication()
    def set_communications_protocol(self, use_line_feed, extended_resolution):
        """Set the instrument communication protocol.

        The driver sets it to Q4 (no line feed and extended resolution) at
        startup.

        """
        if use_line_feed:
            if extended_resolution:
                self.write('Q6')
            else:
                self.write('Q2')
        else:
            if extended_resolution:
                self.write('Q4')
            else:
                self.write('Q0')

    @secure_communication()
    def read_parameter(self, parameter):
        """Read an instrument parameters.

        The possible values of the argument are listed in _PARAMETER_DICT.

        """
        par = _PARAMETER_DICT.get(parameter, None)
        if par:
            return self.query('R{}'.format(par))[1:]
        else:
            raise ValueError(cleandoc(''' Invalid parameter {} sent to
                IPS120-10 read_parameter method'''.format(parameter)))

    def check_connection(self):
        """Check the status of the connection.

        """
        control = self.control
        if (control == 'Local & Locked' or control == 'Local & Unlocked'):
            return False
        else:
            return True

    @instrument_property
    def heater_state(self):
        """State of the switch heater.

        """
        status = self._get_status()
        heat = int(status[8])
        if heat in (0, 2):
            return 'OFF'
        elif heat == 1:
            return 'ON'
        else:
            raise ValueError(cleandoc('''The switch is in fault or absent'''))

    @heater_state.setter
    @secure_communication()
    def heater_state(self, state):
        """State of the switch heater.

        """
        if state == 'ON':
            result = self.query('H1')
            if result.startswith('?'):
                raise InstrIOError(cleandoc('''IPS120-10 did not set the
                    heater state to {}'''.format(state)))
        elif state == 'OFF':
            result = self.query('H0')
            if result.startswith('?'):
                raise InstrIOError(cleandoc('''IPS120-10 did not set the
                    heater state to {}'''.format(state)))
        else:
            raise ValueError(cleandoc(''' Invalid parameter {} sent to
                IPS120-10 set_heater_state method'''.format(state)))
        sleep(1)

    @instrument_property
    def control(self):
        """Parameter determining how the instrument interact with the outside.

        """
        status = self._get_status()
        control = int(status[6])
        state = [k for k, v in _CONTROL_DICT.items() if v == control]
        if state:
            return state[0]
        else:
            return 'Auto-Run-Down'

    @control.setter
    @secure_communication()
    def control(self, control):
        """Parameter determining how the instrument interact with the outside.

        """
        value = _CONTROL_DICT.get(control, None)
        if value:
            result = self.query('C{}'.format(value))
            if result.startswith('?'):
                raise InstrIOError(cleandoc('''IPS120-10 did not set the
                    control to {}'''.format(control)))
        else:
            raise ValueError(cleandoc(''' Invalid parameter {} sent to
                IPS120-10 set_control method'''.format(control)))

    @instrument_property
    def activity(self):
        """Current activity of the power supply (idle, ramping).

        """
        status = self._get_status()
        act = int(status[4])
        return [k for k, v in _ACTIVITY_DICT.items() if v == act][0]

    @activity.setter
    @secure_communication()
    def activity(self, value):
        """Current activity of the power supply (idle, ramping).

        """
        par = _ACTIVITY_DICT.get(value, None)
        if par:
            result = self.query('A{}'.format(par))
            if result.startswith('?'):
                raise InstrIOError(cleandoc('''IPS120-10 did not set the
                    activity to {}'''.format(value)))
        else:
            raise ValueError(cleandoc(''' Invalid parameter {} sent to
                IPS120-10 set_activity method'''.format(value)))

    @instrument_property
    def target_current(self):
        """Current the source tries to reach when going to set point.

        """
        return float(self.read_parameter('Target current'))

    @target_current.setter
    @secure_communication()
    def target_current(self, target):
        """Current the source tries to reach when going to set point.

        """
        result = self.query("I{}".format(target))
        if result.startswith('?'):
            raise InstrIOError(cleandoc('''IPS120-10 did not set the
                    target current to {}'''.format(target)))

    @instrument_property
    def current_sweep_rate(self):
        """Rate at which to sweep the current when the switch heater is on.

        """
        return float(self.read_parameter('Current sweep rate'))

    @current_sweep_rate.setter
    @secure_communication()
    def current_sweep_rate(self, rate):
        """Rate at which to sweep the current when the switch heater is on.

        """
        # amps/min
        result = self.query("S{}".format(rate))
        if result.startswith('?'):
            raise InstrIOError(cleandoc('''IPS120-10 did not set the
                    rate field to {}'''.format(rate)))

    @instrument_property
    def target_field(self):
        """Field the source tries to reach when going to set point.

        """
        return float(self.read_parameter('Target field'))

    @target_field.setter
    @secure_communication()
    def target_field(self, target):
        """Field the source tries to reach when going to set point.

        """
        result = self.query("J{}".format(target))
        if result.startswith('?'):
            raise InstrIOError(cleandoc('''IPS120-10 did not set the
                    target field to {}'''.format(target)))

    @instrument_property
    def field_sweep_rate(self):
        """Rate at which to sweep the field when the switch heater is on.

        """
        return float(self.read_parameter('Field sweep rate'))

    @field_sweep_rate.setter
    @secure_communication()
    def field_sweep_rate(self, rate):
        """Rate at which to sweep the field when the switch heater is on.

        """
        # tesla/min
        result = self.query("T{}".format(rate))
        if result.startswith('?'):
            raise InstrIOError(cleandoc('''IPS120-10 did not set the
                    rate field to {}'''.format(rate)))

    @instrument_property
    def fast_sweep_rate(self):
        """Rate at which to sweep the field when the switch heater is off.

        """
        return float(self.read_parameter('Field sweep rate'))

    @fast_sweep_rate.setter
    @secure_communication()
    def fast_sweep_rate(self, rate):
        """Rate at which to sweep the field when the switch heater is off.

        """
        # tesla/min
        result = self.query("T{}".format(rate))
        if result.startswith('?'):
            raise InstrIOError(cleandoc('''IPS120-10 did not set the
                    rate field to {}'''.format(rate)))

    @secure_communication()
    def _get_status(self):
        """Get the status of the instrument.

        """
        status = self.query('X')
        if status:
            return status.strip()
        else:
            raise InstrIOError('''IPS120-10 did not return its status''')
