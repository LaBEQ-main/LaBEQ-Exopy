# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyHqcLegacy Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Task perform measurements with a VNA.

"""
import time
import re
import numbers
from inspect import cleandoc

import numpy as np
from atom.api import (Str, Int, Bool, Enum, set_default,
                      Value, List)

from exopy.tasks.api import InstrumentTask, TaskInterface, validators


def check_channels_presence(task, channels, *args, **kwargs):
    """ Check that all the channels are correctly defined on the PNA.

    """
    if kwargs.get('test_instr'):
        traceback = {}
        err_path = task.get_error_path()
        with task.test_driver() as instr:
            if instr is None:
                return False, traceback
            channels_present = True
            for channel in channels:
                if channel not in instr.defined_channels:
                    key = err_path + '_' + str(channel)
                    msg = ("Channel {} is not defined in the PNA {}."
                           " Please define it yourself and try again.")
                    traceback[key] = msg.format(channel,
                                                task.selected_instrument[0])

                    channels_present = False

            return channels_present, traceback

    else:
        return True, {}


class PNASetRFFrequencyInterface(TaskInterface):
    """Set the central frequency to be used for the specified channel.

    """
    #: Id of the channel whose central frequency should be set.
    channel = Int(1).tag(pref=True)

    #: Driver for the channel.
    channel_driver = Value()

    def perform(self, frequency=None):
        """Set the central frequency of the specified channel.

        """
        task = self.task
        if not self.channel_driver:
            self.channel_driver = task.driver.get_channel(self.channel)

        task.driver.owner = task.name
        self.channel_driver.owner = task.name

        if frequency is None:
            frequency = task.format_and_eval_string(task.frequency)
            frequency = task.convert(frequency, 'Hz')

        self.channel_driver.frequency = frequency
        task.write_in_database('frequency', frequency)

    def check(self, *args, **kwargs):
        """Make sure the specified channel does exists on the instrument.

        """
        test, tb = super(PNASetRFFrequencyInterface,
                         self).check(*args, **kwargs)
        task = self.task
        res = check_channels_presence(task, [self.channel], *args, **kwargs)
        tb.update(res[1])
        return test and res[0], tb


class PNASetRFPowerInterface(TaskInterface):
    """Set the central power to be used for the specified channel.

    """
    #: Id of the channel whose central frequency should be set.
    channel = Int(1).tag(pref=True)

    #: Port whose output power should be set.
    port = Int(1).tag(pref=True)

    #: Driver for the channel.
    channel_driver = Value()

    def prepare(self):
        """Create the channel driver.

        """
        self.channel_driver = self.task.driver.get_channel(self.channel)

    def perform(self, power=None):
        """Set the power for the selected channel and port.

        """
        task = self.task

        task.driver.owner = task.name
        self.channel_driver.owner = task.name

        if power is None:
            power = task.format_and_eval_string(task.power)

        self.channel_driver.port = self.port
        self.channel_driver.power = power
        task.write_in_database('power', power)

    def check(self, *args, **kwargs):
        """Ensure the presence of the requested channel.

        """
        test, tb = super(PNASetRFPowerInterface, self).check(*args, **kwargs)
        task = self.task
        res = check_channels_presence(task, [self.channel], *args, **kwargs)
        tb.update(res[1])
        return test and res[0], tb


class SingleChannelPNATask(InstrumentTask):
    """Helper class managing the notion of channel in the PNA.

    """
    #: Id of the channel to use.
    channel = Int(1).tag(pref=True)

    channel_driver = Value()

    def prepare(self):
        """Get the channel driver.

        """
        super(SingleChannelPNATask, self).prepare()
        self.channel_driver = self.driver.get_channel(self.channel)

    def check(self, *args, **kwargs):
        """Add checking for channels to the base tests.

        """
        test, traceback = super(SingleChannelPNATask, self).check(*args,
                                                                  **kwargs)
        c_test, c_trace = check_channels_presence(self, [self.channel],
                                                  *args, **kwargs)

        traceback.update(c_trace)
        return test and c_test, traceback


class PNASinglePointMeasureTask(SingleChannelPNATask):
    """Measure the specified parameters. Frequency and power can be set before.

    Wait for any parallel operation before execution.

    """
    #: Id of the channel to use.
    channel = Int(1).tag(pref=True)

    #: Measures to perform.
    measures = List().tag(pref=True)

    #: Bandwith for averaging.
    if_bandwidth = Int(2).tag(pref=True)

    #: Window number in which to display the traces.
    window = Int(1).tag(pref=True)

    wait = set_default({'activated': True, 'wait': ['instr']})

    def perform(self):
        """Prepare the measure and execute it.

        """
        waiting_time = 1.0/self.if_bandwidth

        if self.driver.owner != self.name:
            self.driver.owner = self.name
            self.driver.set_all_chanel_to_hold()
            self.driver.trigger_scope = 'CURRent'
            if self.if_bandwidth >= 5:
                self.driver.trigger_source = 'IMMediate'
            else:
                self.driver.trigger_source = 'MANual'

        meas_names = ['Ch{}:'.format(self.channel) + ':'.join(measure)
                      for measure in self.measures]

        if self.channel_driver.owner != self.name:
            self.channel_driver.owner = self.name
            self.channel_driver.if_bandwidth = self.if_bandwidth
            # Avoid the PNA doing stupid things if it was doing a sweep
            # previously
            freq = self.channel_driver.frequency
            power = self.channel_driver.power
            self.channel_driver.sweep_type = 'LIN'
            self.channel_driver.sweep_points = 1
            self.channel_driver.clear_cache(['frequency', 'power'])
            self.channel_driver.frequency = freq
            self.channel_driver.power = power

            # Check whether or not we are doing the same measures as the ones
            # already defined (avoid losing display optimisation)
            measures = self.channel_driver.list_existing_measures()
            existing_meas = [meas['name'] for meas in measures]

            if not (all([meas in existing_meas for meas in meas_names]) and
                    all([meas in meas_names for meas in existing_meas])):
                clear = True
                self.channel_driver.delete_all_meas()
                for i, meas_name in enumerate(meas_names):
                    self.channel_driver.prepare_measure(meas_name, self.window,
                                                        i+1, clear)
                    clear = False
            if self.if_bandwidth >= 5:
                self.channel_driver.sweep_mode = 'CONTinuous'

        if self.if_bandwidth < 5:
            self.driver.fire_trigger(self.channel)
            time.sleep(waiting_time)
            while not self.driver.check_operation_completion():
                time.sleep(0.1*waiting_time)
        else:
            time.sleep(waiting_time)

        for i, meas_name in enumerate(meas_names):
            self.channel_driver.selected_measure = meas_name
            if self.measures[i][1]:
                data = self.channel_driver.read_formatted_data()[0]
            else:
                data = self.channel_driver.read_raw_data()[0]
            self.write_in_database('_'.join(self.measures[i]), data)

    def check(self, *args, **kwargs):
        """Validate the measure names.

        """
        test, traceback = super(PNASinglePointMeasureTask,
                                self).check(*args, **kwargs)

        pattern = re.compile('S[1-4][1-4]')
        for i, (meas, _) in enumerate(self.measures):
            match = pattern.match(meas)
            if not match:
                path = self.get_error_path()
                path += '_Meas_{}'.format(i)
                traceback[path] = 'Unvalid parameter : {}'.format(meas)
                test = False

        return test, traceback

    def _post_setattr_measures(self, old, new):
        """Update the database based on the measures.

        """
        entries = {}
        for measure in new:
            if measure[1]:
                entries['_'.join(measure)] = 1.0
            else:
                entries[measure[0]] = 1.0 + 1j

        self.database_entries = entries


FEVAL = validators.SkipEmpty(types=numbers.Real)


class PNASweepTask(SingleChannelPNATask):
    """Measure the specified parameters while sweeping either the frequency or
    the power. Measure are saved in an array with named fields : Frequency or
    Power and then 'Measure'_'Format' (S21_MLIN, S33 if Raw)

    Wait for any parallel operation before execution.

    """
    #: Id of the channel to use.
    channel = Int(1).tag(pref=True)

    #: Start value for the sweep.
    start = Str().tag(pref=True, feval=FEVAL)

    #: Stop value for the sweep.
    stop = Str().tag(pref=True, feval=FEVAL)

    #: Number of points desired in the sweep.
    points = Str().tag(pref=True, feval=FEVAL)

    #: Kind of sweep to perform.
    sweep_type = Enum('', 'Frequency', 'Power').tag(pref=True)

    #: Measures to perform.
    measures = List().tag(pref=True)

    #: Bandwith for averaging.
    if_bandwidth = Int(2).tag(pref=True)

    #: Window number in which to display the traces.
    window = Int(1).tag(pref=True)

    wait = set_default({'activated': True, 'wait': ['instr']})
    database_entries = set_default({'sweep_data': np.array([0])})

    def perform(self):
        """Set up the measures and run them.

        """
        if self.driver.owner != self.name:
            self.driver.owner = self.name
            self.driver.set_all_chanel_to_hold()
            self.driver.trigger_scope = 'CURRent'
            self.driver.trigger_source = 'MANual'

        meas_names = ['Ch{}:'.format(self.channel) + ':'.join(measure)
                      for measure in self.measures]

        if self.channel_driver.owner != self.name:
            self.channel_driver.owner = self.name
            if self.if_bandwidth > 0:
                self.channel_driver.if_bandwidth = self.if_bandwidth

            # Check whether or not we are doing the same measures as the ones
            # already defined (avoid losing display optimisation)
            measures = self.channel_driver.list_existing_measures()
            existing_meas = [meas['name'] for meas in measures]

            if not (all([meas in existing_meas for meas in meas_names]) and
                    all([meas in meas_names for meas in existing_meas])):
                clear = True
                self.channel_driver.delete_all_meas()
                for i, meas_name in enumerate(meas_names):
                    self.channel_driver.prepare_measure(meas_name, self.window,
                                                        i+1, clear)
                    clear = False

        current_x_axis = self.channel_driver.sweep_x_axis
        if self.start:
            start = self.format_and_eval_string(self.start)
        else:
            start = current_x_axis[0]*1e9
        if self.stop:
            stop = self.format_and_eval_string(self.stop)
        else:
            stop = current_x_axis[-1]*1e9
        if self.points:
            points = self.format_and_eval_string(self.points)
        else:
            points = len(current_x_axis)
        if self.sweep_type:
            self.channel_driver.prepare_sweep(self.sweep_type.upper(), start,
                                              stop, points)
        else:
            if self.channel_driver.sweep_type.upper() == 'LIN':
                self.channel_driver.prepare_sweep('FREQUENCY',
                                                  start, stop, points)
            elif self.channel_driver.sweep_type.upper() == 'POW':
                self.channel_driver.prepare_sweep('POWER',
                                                  start, stop, points)

        waiting_time = self.channel_driver.sweep_time
        self.driver.fire_trigger(self.channel)
        time.sleep(waiting_time)
        while not self.driver.check_operation_completion():
            time.sleep(0.1*waiting_time)

        data = [np.linspace(start, stop, points)]
        for i, meas_name in enumerate(meas_names):
            if self.measures[i][1]:
                data.append(
                    self.channel_driver.read_formatted_data(meas_name))
            else:
                data.append(self.channel_driver.read_raw_data(meas_name))

        names = [str(self.sweep_type)] + [str('_'.join(meas))
                                          for meas in self.measures]
        final_arr = np.rec.fromarrays(data, names=names)
        self.write_in_database('sweep_data', final_arr)

    def check(self, *args, **kwargs):
        """Validate the measures.

        """
        test, traceback = super(PNASweepTask, self).check(*args, **kwargs)

        pattern = re.compile('S[1-4][1-4]')
        for i, (meas, _) in enumerate(self.measures):
            match = pattern.match(meas)
            if not match:
                path = self.task_path + '/' + self.name
                path += '_Meas_{}'.format(i)
                traceback[path] = 'Unvalid parameter : {}'.format(meas)
                test = False

        data = [np.array([0.0, 1.0])] + \
            [np.array([0.0, 1.0]) for meas in self.measures]
        names = [str(self.sweep_type)] + [str('_'.join(meas))
                                          for meas in self.measures]
        final_arr = np.rec.fromarrays(data, names=names)

        self.write_in_database('sweep_data', final_arr)
        return test, traceback


class PNAGetTraces(InstrumentTask):
    """ Get the traces that are displayed right now (no new acquisition).

    The list of traces to be measured must be entered in the following format
    ch1,tr1;ch2,tr2;ch3,tr3;...
    ex: 1,1;1,3 for ch1, tr1 and ch1, tr3

    """
    #: Traces to get.
    tracelist = Str('1,1').tag(pref=True)

    #: Should the data be measured first.
    already_measured = Bool(False).tag(pref=True)

    database_entries = set_default({'sweep_data': {}})

    def perform(self):
        traces = self.tracelist.split(';')
        tr_data = {}

        if not self.already_measured:
            for i in range(1, 30):
                if str(i)+',' in self.tracelist:
                    self.average_channel(i)

        for trace in traces:
            c_nb, t_nb = trace.split(',')
            tr_data[trace] = self.get_trace(int(c_nb), int(t_nb))

        self.write_in_database('sweep_data', tr_data)

    def average_channel(self, channelnb):
        """Performs the averaging of a channel

        """
        channel_driver = self.driver.get_channel(channelnb)
        channel_driver.run_averaging()

    def get_trace(self, channelnb, tracenb):
        """Get the trace that is displayed right now (no new acquisition)
        on channel and tracenb.

        """
        channel_driver = self.driver.get_channel(channelnb)

        try:
            channel_driver.tracenb = tracenb
        except:
            raise ValueError(cleandoc('''The trace {} does not exist on channel
                                      {}: '''.format(tracenb, channelnb)))

        measname = channel_driver.selected_measure
        data = channel_driver.sweep_x_axis
        complexdata = (channel_driver.read_raw_data(measname) *
                       np.exp(2*np.pi*1j*data*channel_driver.electrical_delay))
        aux = [data, complexdata.real, complexdata.imag,
               np.absolute(complexdata),
               np.unwrap(np.angle(complexdata))]

        return np.rec.fromarrays(aux, names=[str('Freq (GHz)'),
                                             str(measname+' real'),
                                             str(measname+' imag'),
                                             str(measname+' abs'),
                                             str(measname+' phase')])

    def check(self, *args, **kwargs):
        """Create meaningful database entries.

        """
        test, traceback = super(PNAGetTraces, self).check(*args, **kwargs)

        traces = self.tracelist.split(';')
        sweep_data = {}
        for trace in traces:
            data = [np.array([0.0, 1.0]), np.array([1.0, 2.0])]
            sweep_data[trace] = np.rec.fromarrays(data,
                                                  names=[str('a'), str('b')])

        self.write_in_database('sweep_data', sweep_data)
        return test, traceback


class ZNBGetTraces(SingleChannelPNATask):
    """ Get the traces that are displayed right now (no new acquisition).

    """

    database_entries = set_default({'sweep_data': {}})

    def perform(self):
        tr_data = {}
        channels = self.driver.defined_channels
        for channel in channels:
            driverchannel = self.driver.get_channel(channel)
            measures = driverchannel.list_existing_measures()
            x_axis = driverchannel.sweep_x_axis
            for measure in measures:
                meas_name = measure['name']
                data = driverchannel.read_formatted_data(meas_name)
                aux = [x_axis, data]

                names = [str('Freq (GHz)'), str(meas_name+' data')]
                tr_data[meas_name] = np.rec.fromarrays(aux, names=names)

        self.write_in_database('sweep_data', tr_data)

    def check(self, *args, **kwargs):
        """Create meaningful database entries.

        """
        test, traceback = super(ZNBGetTraces, self).check(*args, **kwargs)
        tr_data = {}
        if kwargs.get('test_instr'):
            with self.test_driver() as instr:
                if instr is None:
                    return True, traceback
                channels = instr.defined_channels
                for channel in channels:
                    driverchannel = self.driver.get_channel(channel)
                    measures = driverchannel.list_existing_measures()
                    for measure in measures:
                        meas_name = measure['name']

                        names = [str('Freq (GHz)'), str(meas_name+' data')]
                        fake_data = [np.array([5, 6]), np.array([0, 1])]
                        tr_data[meas_name] = np.rec.fromarrays(fake_data,
                                                               names=names)

        self.write_in_database('sweep_data', tr_data)

        return test, traceback
