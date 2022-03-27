# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyHqcLegacy Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Tasks to handle a signal analyser.

"""
import numbers
from inspect import cleandoc

import numpy as np
from atom.api import (Str, Int, set_default, Enum)


from exopy.tasks.api import InstrumentTask, validators

# XXX unfinished


class PSAGetTrace(InstrumentTask):
    """ Get the trace displayed on the Power Spectrum Analyzer.

    """
    trace = Int(1).tag(pref=True)

    database_entries = set_default({'trace_data': np.array([1.0]),
                                    'psa_config': ''})

    def perform(self):
        """Get the specified trace from the instrument.
        """
        if self.driver.owner != self.name:
            self.driver.owner = self.name

        sweep_modes = {'SA': 'Spectrum Analyzer',
                       'SPEC': 'Basic Spectrum Analyzer',
                       'WAV': 'Waveform'}

        d = self.driver
        header = cleandoc('''Start freq {}, Stop freq {}, Span freq {},
                          Center freq {}, Average number {}, Resolution
                          Bandwidth {}, Video Bandwidth {}, Number of points
                          {}, Mode {}''')
        psa_config = header.format(d.start_frequency_SA, d.stop_frequency_SA,
                                   d.span_frequency, d.center_frequency,
                                   d.average_count_SA, d.RBW, d.VBW_SA,
                                   d.sweep_points_SA, sweep_modes[self.mode])

        self.write_in_database('psa_config', psa_config)
        self.write_in_database('trace_data', self.driver.read_data(self.trace))

    def check(self, *args, **kwargs):
        """Validate the provided trace number.

        """
        test, traceback = super(PSAGetTrace, self).check(*args, **kwargs)

        if self.trace > 4 or self.trace < 1:
            test = False
            msg = 'Trace number should be 1, 2, 3 or 4 not {}'
            traceback[self.get_error_path + '-trace'] = msg.format(self.trace)

        return test, traceback


EMPTY_REAL = validators.SkipEmpty(types=numbers.Real)

EMPTY_INT = validators.SkipEmpty(types=numbers.Integral)


class PSASetParam(InstrumentTask):
    """ Set important parameters of the Power Spectrum Analyzer.

    """
    trace = Int(1).tag(pref=True)

    mode = Enum('Start/Stop', 'Center/Span').tag(pref=True)

    start_freq = Str().tag(pref=True, feval=EMPTY_REAL)

    end_freq = Str().tag(pref=True, feval=EMPTY_REAL)

    center_freq = Str().tag(pref=True, feval=EMPTY_REAL)

    span_freq = Str().tag(pref=True, feval=EMPTY_REAL)

    average_nb = Str().tag(pref=True, feval=EMPTY_INT)

    resolution_bandwidth = Str().tag(pref=True, feval=EMPTY_REAL)

    video_bandwidth = Str().tag(pref=True, feval=EMPTY_REAL)

    database_entries = set_default({'psa_config': ''})

    def perform(self):
        """Set the specified parameters.

        """
        if self.driver.owner != self.name:
            self.driver.owner = self.name

        if self.mode == 'Start/Stop':
            if self.start_freq:
                self.driver.start_frequency_SA = \
                    self.format_and_eval_string(self.start_freq)

            if self.stop_freq:
                self.driver.stop_frequency_SA = \
                    self.format_and_eval_string(self.stop_freq)

            # start_freq is set again in case the former value of stop
            # prevented to do it
            if self.start_freq:
                self.driver.start_frequency_SA = \
                    self.format_and_eval_string(self.start_freq)
        else:
            if self.center_freq:
                self.driver.center_frequency = \
                    self.format_and_eval_string(self.center_freq)

            if self.span_freq:
                self.driver.span_frequency = \
                    self.format_and_eval_string(self.span_freq)

            # center_freq is set again in case the former value of span
            # prevented to do it
            if self.center_freq:
                self.driver.center_frequency = \
                    self.format_and_eval_string(self.center_freq)

        if self.average_nb:
            self.driver.average_count_SA = \
                self.format_and_eval_string(self.average_nb)

        if self.resolution_bandwidth:
            self.driver.RBW = \
                self.format_and_eval_string(self.resolution_bandwidth)

        if self.video_bandwidth:
            self.driver.VBW_SA = \
                self.format_and_eval_string(self.video_bandwidth)

        sweep_modes = {'SA': 'Spectrum Analyzer',
                       'SPEC': 'Basic Spectrum Analyzer',
                       'WAV': 'Waveform'}

        d = self.driver
        psa_config = '''Start freq {}, Stop freq {}, Span freq {}, Center freq
                     {}, Average number {}, Resolution Bandwidth {},
                     Video Bandwidth {}, Number of points {}, Mode
                     {}'''.format(d.start_frequency_SA, d.stop_frequency_SA,
                                  d.span_frequency, d.center_frequency,
                                  d.average_count_SA, d.RBW, d.VBW_SA,
                                  d.sweep_points_SA, sweep_modes[self.mode])

        self.write_in_database('psa_config', psa_config)

    def check(self, *args, **kwargs):
        """
        """
        test, traceback = super(PSAGetTrace, self).check(*args, **kwargs)

        err_path = self.get_error_path()

        if kwargs.get('test_instr'):
            if self.driver.mode != 'SA':
                test = False
                traceback[err_path] = 'PSA is not in Spectrum Analyzer mode'

        if self.mode == 'Start/Stop':
            try:
                if self.start_freq:
                    start = self.format_and_eval_string(self.start_freq)
# if type(self.driver).__name__ == 'AgilentPSA':
# is a new PSA needs to be encoded, it would be best to use task_interfaces
                    if (start < 3) or (start > 26500000000):
                        raise Exception('out_of_range')

            except Exception as e:
                test = False
                if e.args == 'out_of_range':
                    traceback[err_path +
                              '-start_freq'] = 'Start frequency {} out of ' + \
                        'range'.format(self.start_freq)
                else:
                    traceback[err_path +
                              '-start_freq'] = 'Failed to eval the start' + \
                        'formula {}'.format(self.start_freq)

            try:
                if self.stop_freq:
                    toto = self.format_and_eval_string(self.stop_freq)
                    if (toto < 3) or (toto > 26500000000):
                        raise Exception('out_of_range')

            except Exception as e:
                test = False
                if e.args == 'out_of_range':
                    traceback[err_path +
                              '-stop_freq'] = 'Stop frequency {} out of ' + \
                        'range'.format(self.start_freq)
                else:
                    traceback[err_path +
                              '-stop_freq'] = 'Failed to eval the stop' + \
                        'formula {}'.format(self.stop_freq)
        else:
            try:
                if self.span_freq:
                    toto = self.format_and_eval_string(self.span_freq)
                    if (toto < 0) or (toto > 26500000000):
                        raise Exception('out_of_range')

            except Exception as e:
                test = False
                if e.args == 'out_of_range':
                    traceback[err_path +
                              '-span_freq'] = 'Span frequency {} out of ' + \
                        'range'.format(self.span_freq)
                else:
                    traceback[err_path +
                              '-span_freq'] = 'Failed to eval the span' + \
                        'formula {}'.format(self.span_freq)

            try:
                if self.center_freq:
                    toto = self.format_and_eval_string(self.center_freq)
                    if (toto < 3) or (toto > 26500000000):
                        raise Exception('out_of_range')

            except Exception as e:
                test = False
                if e.args == 'out_of_range':
                    traceback[err_path +
                              '-center_freq'] = 'Center frequency {} out of ' + \
                        'range'.format(self.center_freq)
                else:
                    traceback[err_path +
                              '-center_freq'] = 'Failed to eval the stop' + \
                        'formula {}'.format(self.center_freq)

        try:
            if self.average_nb:
                toto = self.format_and_eval_string(self.average_nb)
                if (toto < 1) or (toto > 8192):
                    raise Exception('out_of_range')

        except Exception as e:
            test = False
            if e.args == 'out_of_range':
                traceback[err_path +
                          '-average_nb'] = 'Average number {} out of ' + \
                    'range'.format(self.average_nb)
            else:
                traceback[err_path +
                          '-average_nb'] = 'Failed to eval the average_nb' + \
                    'formula {}'.format(self.average_nb)

        try:
            if self.average_nb:
                toto = self.format_and_eval_string(self.resolution_bandwidth)
                if (toto < 1) or (toto > 8000000):
                    raise Exception('out_of_range')

        except Exception as e:
            test = False
            if e.args == 'out_of_range':
                traceback[err_path +
                          '-resolution_bandwidth'] = 'Resolution BW number' + \
                    '{} out of range'.format(self.average_nb)
            else:
                traceback[err_path +
                          '-resolution_bandwidth'] = 'Failed to eval the ' + \
                    'resolution_bandwidth formula {}' + \
                    ''.format(self.resolution_bandwidth)

        try:
            if self.average_nb:
                toto = self.format_and_eval_string(self.video_bandwidth)
                if (toto < 1) or (toto > 50000000):
                    raise Exception('out_of_range')

        except Exception as e:
            test = False
            if e.args == 'out_of_range':
                traceback[err_path +
                          '-video_bandwidth'] = 'Video BW number' + \
                    '{} out of range'.format(self.video_bandwidth)
            else:
                traceback[err_path +
                          '-video_bandwidth'] = 'Failed to eval the ' + \
                    'video_bandwidth formula {}' + \
                    ''.format(self.video_bandwidth)

        return test, traceback
