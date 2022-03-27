# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyHqcLegacy Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Task perform measurements the SPDevices digitizers.

"""
import numbers
import numpy as np
from atom.api import (Bool, Str, Enum, set_default)

from exopy.tasks.api import InstrumentTask, validators

VAL_REAL = validators.Feval(types=numbers.Real)

VAL_INT = validators.Feval(types=numbers.Integral)


class DemodSPTask(InstrumentTask):
    """Get the averaged quadratures of the signal.

    """

    # No avg: return raw traces/I,Q pairs,
    # Avg before demod: average raw traces, then return
    # averaged trace / average I,Q
    # Avg after demod: calculate one I,Q per trace, then average.
    # This allows to use a ref Iref,Qref
    # and correct each I,Q pair by the ref, then average
    average = Enum('No avg', 'Avg before demod',
                   'Avg after demod').tag(pref=True)

    #: Number of loops in the pulse sequence
    num_loop = Str('1').tag(pref=True, feval=VAL_INT)

    #: Should the acquisition on channel 1 be enabled
    ch1_enabled = Bool(True).tag(pref=True)

    #: Should the acquisition on channel 2 be enabled
    ch2_enabled = Bool(True).tag(pref=True)

    #: Should the full trace be written in the database
    ch1_trace = Bool(False).tag(pref=True)

    #: Should the full trace be written in the database
    ch2_trace = Bool(False).tag(pref=True)

    #: Frequency of the signal sent to channel 1 in MHz
    freq_1 = Str('50').tag(pref=True, feval=VAL_REAL)

    #: Frequency of the signal sent to channel 2 in MHz
    freq_2 = Str('50').tag(pref=True, feval=VAL_REAL)

    #: Time during which to acquire data after a trigger (ns).
    duration = Str('1000').tag(pref=True, feval=VAL_REAL)

    #: Time to wait after a trigger before starting acquisition (ns).
    delay = Str('0').tag(pref=True, feval=VAL_REAL)

    #: Number of records to acquire (one per trig)
    records_number = Str('1000').tag(pref=True, feval=VAL_INT)

    #: Reference: when using average after demod, we can use ch2 as a ref, and
    # correct every I,Q from ch1 by Iref, Qref from ch2. This interferometric
    # measurement eliminates many sources of noise
    ref2 = Bool(False).tag(pref=True)

    #: Sampling rate in samples per second
    sampling_rate = Str('500000000').tag(pref=True, feval=VAL_INT)

    database_entries = set_default({'Ch1_I': 1.0, 'Ch1_Q': 1.0,
                                    'Ch2_I': 1.0, 'Ch2_Q': 1.0})

    def check(self, *args, **kwargs):
        """Check that parameters make sense.

        """
        test, traceback = super(DemodSPTask, self).check(*args, **kwargs)

        if not test:
            return test, traceback

        locs = {}
        to_eval = (('duration',) + (('freq_1',) if self.ch1_enabled else ()) +
                   (('freq_2',) if self.ch2_enabled else ()))
        for n in to_eval:
            locs[n] = self.format_and_eval_string(getattr(self, n))

        p1 = locs['freq_1']*locs['duration']*1e-3 if self.ch1_enabled else 1.
        p2 = locs['freq_2']*locs['duration']*1e-3 if self.ch2_enabled else 1.
        #  THIS CHECK DOES NOT WORK FOR ALAZAR. We need to recalculate the nb
        #  of samples per trace so that it is multiple of 32. The nb of samples
        #  is hence modified after this check is performed.
        if (not p1.is_integer() or not p2.is_integer()):
            msg = ('The duration must be an integer times the period of the '
                   'demodulations. The duration will be truncated to match '
                   'this constraint')
            traceback[self.get_error_path() + '-' + n] = msg

        sampling_rate = self.format_and_eval_string(self.sampling_rate)
        s1 = sampling_rate % locs['freq_1']*1e6 if self.ch1_enabled else 0
        s2 = sampling_rate % locs['freq_2']*1e6 if self.ch2_enabled else 0
        if s1 or s2:
            test = False
            msg = ('The sampling rate must be a multiple of the demodulation '
                   'frequency.')
            traceback[self.get_error_path() + '-' + n] = msg

        if self.ch1_enabled and self.ch1_trace:
            phi1 = np.linspace(0, 2*np.pi*locs['freq_1']*locs['duration'], p1)
            self.write_in_database('Ch1_trace', np.sin(phi1))
        if self.ch2_enabled and self.ch2_trace:
            phi2 = np.linspace(0, 2*np.pi*locs['freq_2']*locs['duration'], p2)
            self.write_in_database('Ch2_trace', np.sin(phi2))

        if ((self.ref2 and self.average == 'Avg before demod') or
                (self.ref2 and not (self.ch1_enabled and self.ch2_enabled))):
            test = False
            msg = ('Using channel 2 as ref requires not to average before '
                   'demod and both channel to be enabled')
            traceback[self.get_error_path() + '-reference'] = msg

        return test, traceback

    def perform(self):
        """Acquire the averaged trace and compute the demodulated
        signal for both channels.

        """
        if self.driver.owner != self.name:
            self.driver.owner = self.name
            self.driver.configure_board()

        avg_bef_demod = self.average == 'Avg before demod'
        avg_aft_demod = self.average == 'Avg after demod'

        num_loop = int(self.format_and_eval_string(self.num_loop))
        records_number = self.format_and_eval_string(self.records_number)
        records_number *= num_loop
        delay = self.format_and_eval_string(self.delay)*1e-9
        duration = self.format_and_eval_string(self.duration)*1e-9
        sampling_rate = self.format_and_eval_string(self.sampling_rate)

        channels = (self.ch1_enabled, self.ch2_enabled)

        traces = self.driver.get_traces(channels, duration, delay,
                                        records_number, average=avg_bef_demod)

        def treat_channel_data(index):
            """Treat the data of a channel.

            """
            ch = traces[index-1]
            freq = self.format_and_eval_string(getattr(self,
                                                       'freq_%d' % index))*1e6

            # Remove points that do not belong to a full period.
            samples_per_period = int(sampling_rate/freq)
            samples_per_trace = int(ch.shape[-1])
            if (samples_per_trace % samples_per_period) != 0:
                extra = samples_per_trace % samples_per_period
                ch = ch.T[:-extra].T

            if not avg_bef_demod:
                ntraces, nsamples = np.shape(ch)
                ch = ch.reshape(int(ntraces/num_loop), num_loop, nsamples)
            else:
                nsamples = np.shape(ch)[0]
            phi = np.linspace(0, 2*np.pi*freq*((nsamples-1)*2e-9), nsamples)
            cosin = np.cos(phi)
            sinus = np.sin(phi)
            # The mean value of cos^2 is 0.5 hence the factor 2 to get the
            # amplitude.
            if not avg_bef_demod:
                ch_i = 2*np.mean(ch*cosin, axis=2)
                ch_q = 2*np.mean(ch*sinus, axis=2)
                ch_i_av = ch_i.T[0] if not avg_aft_demod else np.mean(ch_i,
                                                                      axis=0)
                ch_q_av = ch_q.T[0] if not avg_aft_demod else np.mean(ch_q,
                                                                      axis=0)
            else:
                ch_i = None
                ch_q = None
                ch_i_av = 2*np.mean(ch*cosin)
                ch_q_av = 2*np.mean(ch*sinus)
            self.write_in_database('Ch%d_I' % index, ch_i_av)
            self.write_in_database('Ch%d_Q' % index, ch_q_av)

            if getattr(self, 'ch%d_trace' % index):
                ch_av = ch if not avg_aft_demod else np.mean(ch, axis=0)
                self.write_in_database('Ch%d_trace' % index, ch_av)

            return freq, cosin, sinus, ch_i, ch_q

        if self.ch1_enabled:
            freq, cosin, sinus, ch1_i, ch1_q = treat_channel_data(1)

        if self.ch2_enabled:
            _, _, _, ch2_i, ch2_q = treat_channel_data(2)

        if self.ref2:
            ch2_c = ch2_i + 1j*ch2_q
            normed = (ch1_i + 1j*ch1_q)/ch2_c
            chc_i = np.real(normed)
            chc_q = np.imag(normed)
            # TODO ZL RL: quick fix for single shot data, need to do this
            # properly chc_i.T[0]
            chc_i_av = chc_i if not avg_aft_demod else np.mean(chc_i, axis=0)
            chc_q_av = chc_q if not avg_aft_demod else np.mean(chc_q, axis=0)
            self.write_in_database('Chc_I', chc_i_av)
            self.write_in_database('Chc_Q', chc_q_av)
            if self.ch1_trace:
                ch1 = traces[0]
                ntraces1, _ = np.shape(ch1)
                samples_per_period = int(sampling_rate/freq)

                samples_per_trace = int(ch1.shape[-1])
                ch1_c1 = ch1*cosin
                ch1_s1 = ch1*sinus

                # We crunch a single dimension to compute I and Q per period
                shape = (int(ntraces1/num_loop), num_loop,
                         samples_per_trace//(samples_per_period),
                         samples_per_period)

                ch1_c1 = ch1_c1.reshape(shape)
                ch1_i_t = 2*np.mean(ch1_c1, axis=3)
                ch1_s1 = ch1_s1.reshape(shape)
                ch1_q_t = 2*np.mean(ch1_s1, axis=3)

                ch1_c_t = ch1_i_t + 1j*ch1_q_t
                chc_c_t = np.swapaxes(np.swapaxes(ch1_c_t, 0, 2)/ch2_c.T, 0, 2)
                chc_i_t = np.real(chc_c_t)
                chc_q_t = np.imag(chc_c_t)

                if not avg_aft_demod:
                    chc_i_t_av = np.swapaxes(chc_i_t, 0, 1)[0]
                    chc_q_t_av = np.swapaxes(chc_q_t, 0, 1)[0]
                else:
                    chc_i_t_av = np.mean(chc_i_t, axis=0)
                    chc_q_t_av = np.mean(chc_q_t, axis=0)

                self.write_in_database('Chc_I_trace', chc_i_t_av)
                self.write_in_database('Chc_Q_trace', chc_q_t_av)

    def _post_setattr_ch1_enabled(self, old, new):
        """Update the database entries based on the enabled channels.

        """
        entries = {'Ch1_I': 1.0, 'Ch1_Q': 1.0}
        if self.ref2 and self.ch2_enabled:
            entries.update({'Chc_I': 1.0, 'Chc_Q': 1.0})
        if self.ch1_trace:
            entries['Ch1_trace'] = np.array([0, 1])
            if self.ref2 and self.ch2_enabled:
                entries['Chc_I_trace'] = np.array([0, 1])
                entries['Chc_Q_trace'] = np.array([0, 1])
        self._update_entries(new, entries)

    def _post_setattr_ch2_enabled(self, old, new):
        """Update the database entries based on the enabled channels.

        """
        entries = {'Ch2_I': 1.0, 'Ch2_Q': 1.0}
        if self.ref2 and self.ch1_enabled:
            entries.update({'Chc_I': 1.0, 'Chc_Q': 1.0})
        if self.ch2_trace:
            entries['Ch2_trace'] = np.array([0, 1])
        if (self.ref2 and self.ch1_enabled) and self.ch1_trace:
            entries['Chc_I_trace'] = np.array([0, 1])
            entries['Chc_Q_trace'] = np.array([0, 1])
        if not self.ch2_enabled:
            self.ref2 = False
        self._update_entries(new, entries)

    def _post_setattr_ch1_trace(self, old, new):
        """Update the database entries based on the trace setting.

        """
        if new and not self.ch1_enabled:
            return
        self._update_entries(new, {'Ch1_trace': np.array([0, 1])})
        if self.ref2:
            self._update_entries(new, {'Chc_I_trace': np.array([0, 1]),
                                       'Chc_Q_trace': np.array([0, 1])})

    def _post_setattr_ch2_trace(self, old, new):
        """Update the database entries based on the trace settings.

        """
        if new and not self.ch2_enabled:
            return
        self._update_entries(new, {'Ch2_trace': np.array([0, 1])})

    def _post_setattr_ref2(self, old, new):
        """Update the database entries based on the ref2 settings.

        """
        self._update_entries(new, {'Chc_I': 1.0, 'Chc_Q': 1.0})
        if self.ch1_trace:
            self._update_entries(new, {'Chc_I_trace': np.array([0, 1]),
                                       'Chc_Q_trace': np.array([0, 1])})

    def _update_entries(self, new, defaults):
        """Update database entries.

        """
        entries = self.database_entries.copy()
        if new:
            entries.update(defaults)
        else:
            for e in defaults:
                if e in entries:
                    del entries[e]
        self.database_entries = entries
