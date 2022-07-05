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

from atom.api import (Float, Value, Str, Int, set_default, Tuple, Enum)

from exopy.tasks.api import (InstrumentTask, TaskInterface,
                            InterfaceableTaskMixin, validators)


class SetDCVoltageTask(InstrumentTask):
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
    database_entries = set_default({'voltage': 0.00})

    wait = set_default({'activated': True, 'wait': ['instr']})

    def perform(self):


        if hasattr(self.driver, 'function') and\
                self.driver.function != 'VOLT':
            msg = ('Instrument assigned to task {} is not configured to '
                    'output a voltage')
            raise ValueError(msg.format(self.name))

        voltage = self.format_and_eval_string(self.target_value)
        self.driver.set_voltage(voltage)
        self.write_in_database('voltage', voltage)

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


class SetDCCurrentTask(InstrumentTask):
    """Set a DC current to the specified value.

    The user can choose to limit the rate by choosing an appropriate back step
    (larger step allowed), and a waiting time between each step.

    """
    #: Target value for the source (dynamically evaluated)
    target_value = Str().tag(pref=True)

    #: Largest allowed step when changing the output of the instr.
    back_step = Float().tag(pref=True)

    #: Largest allowed current
    safe_max = Float(0.0).tag(pref=True)

    #: Time to wait between changes of the output of the instr.
    delay = Float(0.01).tag(pref=True)

    parallel = set_default({'activated': True, 'pool': 'instr'})
    database_entries = set_default({'current': 0.00})

    wait = set_default({'activated': True, 'wait': ['instr']})

    def perform(self):
        """Default interface.

        """

        if hasattr(self.driver, 'function') and\
                self.driver.function != 'CURR':
            msg = ('Instrument assigned to task {} is not configured to '
                    'output a current')
            raise ValueError(msg.format(self.name))
        
        current = self.format_and_eval_string(self.target_value)
        self.driver.set_current(current)
        self.write_in_database('current', current)

class SetDCFunctionTask(InstrumentTask):
    """Set a DC source function to the specified value: VOLT or CURR

    """
    #: Target value for the source (dynamically evaluated)
    switch = Enum('VOLT','CURR').tag(pref=True)

    database_entries = set_default({'function': 'VOLT'})

    wait = set_default({'activated': True, 'wait': ['instr']})

    def perform(self):
        """Default interface.

        """

        mode = self.switch
        if mode == 'VOLT':
            self.driver.set_function(mode)
            self.write_in_database('function', 'VOLT')

        if mode == 'CURR':
            self.driver.set_function(mode)
            self.write_in_database('function', 'CURR')


class SetDCOutputTask(InstrumentTask):
    """Set a DC source output to the specified value: ON or OFF

    """
    #: Target value for the source output
    mode = Enum('OFF', 'ON').tag(pref=True)

    database_entries = set_default({'output': 'None'})

    wait = set_default({'activated': True, 'wait': ['instr']})

    def perform(self):
        """Default interface.

        """
        if self.mode == 'ON':
            self.driver.set_output("ON")
            self.write_in_database('output', 'ON')

        elif self.mode == 'OFF':
            self.driver.set_output("OFF")
            self.write_in_database('output', 'OFF')
