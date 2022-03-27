# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyHqcLegacy Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Task to set the parameters of microwave sources..

"""
import time
import numbers

from atom.api import (Float, Value, Str, Int, set_default, Tuple)

from exopy.tasks.api import (InstrumentTask, TaskInterface,
                            InterfaceableTaskMixin, validators)


class SetDCVoltageTask(InterfaceableTaskMixin, InstrumentTask):
    """Set a DC voltage to the specified value.

    The user can choose to limit the rate by choosing an appropriate back step
    (larger step allowed), and a waiting time between each step.

    """
    #: Target value for the source (dynamically evaluated)
    target_value = Str().tag(pref=True, feval=validators.SkipLoop(types=numbers.Real))

    #: Largest allowed step when changing the output of the instr.
    back_step = Float().tag(pref=True)

    #: Largest allowed voltage
    safe_max = Float(0.0).tag(pref=True)

    #: Largest allowed delta compared to current voltage. 0 = ignored
    safe_delta = Float(0.0).tag(pref=True)

    #: Time to wait between changes of the output of the instr.
    delay = Float(0.01).tag(pref=True)

    parallel = set_default({'activated': True, 'pool': 'instr'})
    database_entries = set_default({'voltage': 0.01})

    def i_perform(self, value=None):
        """Default interface.

        """
        if self.driver.owner != self.name:
            self.driver.owner = self.name
            if hasattr(self.driver, 'function') and\
                    self.driver.function != 'VOLT':
                msg = ('Instrument assigned to task {} is not configured to '
                       'output a voltage')
                raise ValueError(msg.format(self.name))

        setter = lambda value: setattr(self.driver, 'voltage', value)
        current_value = getattr(self.driver, 'voltage')

        self.smooth_set(value, setter, current_value)

    def smooth_set(self, target_value, setter, current_value):
        """ Smoothly set the voltage.

        target_value : float
            Voltage to reach.

        setter : callable
            Function to set the voltage, should take as single argument the
            value.

        current_value: float
            Current voltage.

        """
        if target_value is not None:
            value = target_value
        else:
            value = self.format_and_eval_string(self.target_value)

        if self.safe_delta and abs(current_value-value) > self.safe_delta:
            msg = ('Requested voltage {} is too far away from the current voltage {}!')
            raise ValueError(msg.format(value, current_value))

        if self.safe_max and self.safe_max < abs(value):
            msg = 'Requested voltage {} exceeds safe max : {}'
            raise ValueError(msg.format(value, self.safe_max))

        last_value = current_value

        if abs(last_value - value) < 1e-12:
            self.write_in_database('voltage', value)
            return

        elif self.back_step == 0:
            self.write_in_database('voltage', value)
            setter(value)
            return

        else:
            if (value - last_value)/self.back_step > 0:
                step = self.back_step
            else:
                step = -self.back_step

        if abs(value-last_value) > abs(step):
            while not self.root.should_stop.is_set():
                # Avoid the accumulation of rounding errors
                last_value = round(last_value + step, 9)
                setter(last_value)
                if abs(value-last_value) > abs(step):
                    time.sleep(self.delay)
                else:
                    break

        if not self.root.should_stop.is_set():
            setter(value)
            self.write_in_database('voltage', value)
            return

        self.write_in_database('voltage', last_value)


class MultiChannelVoltageSourceInterface(TaskInterface):
    """Interface for multiple outputs sources.

    """
    #: Id of the channel to use.
    channel = Tuple(default=(1, 1)).tag(pref=True)

    #: Reference to the driver for the channel.
    channel_driver = Value()

    def perform(self, value=None):
        """Set the specified voltage.

        """
        task = self.task
        if not self.channel_driver:
            self.channel_driver = task.driver.get_channel(self.channel)
        if self.channel_driver.owner != task.name:
            self.channel_driver.owner = task.name
            if hasattr(self.channel_driver, 'function') and\
                    self.channel_driver.function != 'VOLT':
                msg = ('Instrument output assigned to task {} is not '
                       'configured to output a voltage')
                raise ValueError(msg.format(self.name))

        setter = lambda value: setattr(self.channel_driver, 'voltage', value)
        current_value = getattr(self.channel_driver, 'voltage')

        task.smooth_set(value, setter, current_value)

    def check(self, *args, **kwargs):
        if kwargs.get('test_instr'):
            task = self.task
            traceback = {}
            with task.test_driver() as d:
                if d is None:
                    return True, {}
                if self.channel not in d.defined_channels:
                    key = task.get_error_path() + '_interface'
                    traceback[key] = 'Missing channel {}'.format(self.channel)

            if traceback:
                return False, traceback
            else:
                return True, traceback

        else:
            return True, {}


class SetDCCurrentTask(InterfaceableTaskMixin, InstrumentTask):
    """Set a DC current to the specified value.

    The user can choose to limit the rate by choosing an appropriate back step
    (larger step allowed), and a waiting time between each step.

    """
    #: Target value for the source (dynamically evaluated)
    target_value = Str().tag(pref=True, feval=validators.SkipLoop(types=numbers.Real))

    #: Largest allowed step when changing the output of the instr.
    back_step = Float().tag(pref=True)

    #: Largest allowed current
    safe_max = Float(0.0).tag(pref=True)

    #: Time to wait between changes of the output of the instr.
    delay = Float(0.01).tag(pref=True)

    parallel = set_default({'activated': True, 'pool': 'instr'})
    database_entries = set_default({'current': 0.01})

    def i_perform(self, value=None):
        """Default interface.

        """
        if self.driver.owner != self.name:
            self.driver.owner = self.name
            if hasattr(self.driver, 'function') and\
                    self.driver.function != 'CURR':
                msg = ('Instrument assigned to task {} is not configured to '
                       'output a current')
                raise ValueError(msg.format(self.name))

        setter = lambda value: setattr(self.driver, 'current', value)
        current_value = getattr(self.driver, 'current')

        self.smooth_set(value, setter, current_value)

    def smooth_set(self, target_value, setter, current_value):
        """ Smoothly set the current.

        target_value : float
            Current to reach.

        setter : callable
            Function to set the current, should take as single argument the
            value.

        """
        if target_value is not None:
            value = target_value
        else:
            value = self.format_and_eval_string(self.target_value)

        if self.safe_max and self.safe_max < abs(value):
            msg = 'Requested current {} exceeds safe max : {}'
            raise ValueError(msg.format(value, self.safe_max))

        last_value = current_value

        if abs(last_value - value) < 1e-12:
            self.write_in_database('current', value)
            return

        elif self.back_step == 0:
            self.write_in_database('current', value)
            setter(value)
            return

        else:
            if (value - last_value)/self.back_step > 0:
                step = self.back_step
            else:
                step = -self.back_step

        if abs(value-last_value) > abs(step):
            while not self.root.should_stop.is_set():
                # Avoid the accumulation of rounding errors
                last_value = round(last_value + step, 9)
                setter(last_value)
                if abs(value-last_value) > abs(step):
                    time.sleep(self.delay)
                else:
                    break

        if not self.root.should_stop.is_set():
            setter(value)
            self.write_in_database('current', value)
            return

        self.write_in_database('current', last_value)


class SetDCFunctionTask(InterfaceableTaskMixin, InstrumentTask):
    """Set a DC source function to the specified value: VOLT or CURR

    """
    #: Target value for the source (dynamically evaluated)
    switch = Str('VOLT').tag(pref=True, feval=validators.SkipLoop())

    database_entries = set_default({'function': 'VOLT'})

    def i_perform(self, switch=None):
        """Default interface.

        """
        if switch is None:
            switch = self.format_and_eval_string(self.switch)

        if switch == 'VOLT':
            self.driver.function = 'VOLT'
            self.write_in_database('function', 'VOLT')

        if switch == 'CURR':
            self.driver.function = 'CURR'
            self.write_in_database('function', 'CURR')


class SetDCOutputTask(InterfaceableTaskMixin, InstrumentTask):
    """Set a DC source output to the specified value: ON or OFF

    """
    #: Target value for the source output
    switch = Str('OFF').tag(pref=True)

    database_entries = set_default({'output': 'OFF'})

    def i_perform(self, switch=None):
        """Default interface.

        """
        if self.switch == 'ON':
            self.driver.output = 'ON'
            self.write_in_database('output', 'ON')

        elif self.switch == 'OFF':
            self.driver.output = 'OFF'
            self.write_in_database('output', 'OFF')
