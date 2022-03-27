# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyHqcLegacy Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""This module defines drivers for Alazar using DLL Library.

:Contains:
    Alazar935x

Visual C++ runtime needs to be installed to be able to load the dll.

"""
import sys
import math
from subprocess import call

import numpy as np

from ..dll_tools import DllInstrument
from ..driver_tools import InstrIOError
from . import atsapi as ats


class Alazar935x(DllInstrument):
    """Driver for Alazar cards of the 935x series.

    """

    library = 'ATSApi.dll'

    def __init__(self, connection_infos, caching_allowed=True,
                 caching_permissions={}, auto_open=True):

        super(Alazar935x, self).__init__(connection_infos, caching_allowed,
                                         caching_permissions, auto_open)

        if auto_open:
            self.open_connection()

    def open_connection(self):
        """Close Alazar app and create the underlying driver.

        """
        try:
            if sys.platform == 'win32':
                call("TASKKILL /F /IM AlazarDSO.exe", shell=True)
        except Exception:
            pass
        self.board = ats.Board()

    def close_connection(self):
        """Do not need to close a connection

        """
        pass

    def configure_board(self):
        """Set standard parameters.

        """
        board = self.board
        self.samples_per_sec = 500000000
        board.setCaptureClock(ats.EXTERNAL_CLOCK_10MHz_REF,
                              self.samples_per_sec,
                              ats.CLOCK_EDGE_RISING,
                              1)

        board.inputControl(ats.CHANNEL_A,
                           ats.AC_COUPLING,
                           ats.INPUT_RANGE_PM_200_MV,
                           ats.IMPEDANCE_50_OHM)

        board.setBWLimit(ats.CHANNEL_A, 0)

        board.inputControl(ats.CHANNEL_B,
                           ats.AC_COUPLING,
                           ats.INPUT_RANGE_PM_100_MV,
                           ats.IMPEDANCE_50_OHM)

        board.setBWLimit(ats.CHANNEL_B, 0)

        board.setTriggerOperation(ats.TRIG_ENGINE_OP_J,
                                  ats.TRIG_ENGINE_J,
                                  ats.TRIG_EXTERNAL,
                                  ats.TRIGGER_SLOPE_POSITIVE,
                                  150,
                                  ats.TRIG_ENGINE_K,
                                  ats.TRIG_DISABLE,
                                  ats.TRIGGER_SLOPE_POSITIVE,
                                  128)

        board.setExternalTrigger(ats.DC_COUPLING, ats.ETR_5V)

        triggerDelay_sec = 0
        triggerDelay_samples = 4*int(triggerDelay_sec*self.samples_per_sec/4)
        board.setTriggerDelay(triggerDelay_samples)

        board.setTriggerTimeOut(0)

        board.configureAuxIO(ats.AUX_OUT_TRIGGER,
                             0)

    def get_traces(self, channels, duration, delay, records_per_capture,
                   retry=True, average=False):
        """Acquire traces and average if asked to.

        Parameters
        ----------
        channels : tuple
            Tuple of boolean indicating which channels are active.

        duration : float
            Time during which to acquire the data (in seconds)

        delay : float
            Time to wait after a trigger before starting next measure
            (in seconds).

        records_per_capture : int
            Number of records to acquire (per channel)

        retry : bool, optional
            Should acquisition be tried again if first attempt fails.

        average : bool, optional
            Should traces be averaged.

        Returns
        -------
        data : list
            List containing the acquired data per channel, average or not based
            on the average parameter.

        """
        board = self.board

        triggerDelay_sec = delay
        triggerDelay_samples = 4*int(triggerDelay_sec*self.samples_per_sec/4)
        board.setTriggerDelay(triggerDelay_samples)

        # Acquired only specified channels

        channel_count = channels[0] + channels[1]
        cA = ats.CHANNEL_A if channels[0] else 0
        cB = ats.CHANNEL_B if channels[1] else 0
        channels_tuple = channels
        channels = cA | cB

        post_trigger_samples = int(self.samples_per_sec*duration)
        if post_trigger_samples % 32 == 0:
            post_trigger_samples = int(post_trigger_samples)
        else:
            post_trigger_samples = int((post_trigger_samples)/32 + 1)*32
        # Determine the number of records per buffer
        memory_size_samples, bits_per_sample = board.getChannelInfo()

        # No pre-trigger samples in NPT mode
        pre_trigger_samples = 0
        bytes_per_sample = (bits_per_sample.value + 7) // 8

        samples_per_record = pre_trigger_samples + post_trigger_samples
        bytes_per_record = bytes_per_sample * samples_per_record

        # See remark page 93 in ATS-SDK-Guide 7.1.4
        # + following email exchange with Alazar
        # engineer Romain Deterre
        bytes_per_buffer_max = 1e6
        rPB = int(bytes_per_buffer_max // (bytes_per_record * channel_count))
        records_per_buffer = np.min([rPB, records_per_capture])
        bytes_per_buffer = bytes_per_record*records_per_buffer*channel_count

        buffers_per_acquisition = int(math.ceil(records_per_capture /
                                                records_per_buffer))
        records_to_ignore = (buffers_per_acquisition*records_per_buffer -
                             records_per_capture)

        buffer_count = 4
        # Allocate DMA buffers
        buffers = []
        for i in range(buffer_count):
            buffers.append(ats.DMABuffer(bytes_per_sample, bytes_per_buffer))

        # Set the record size
        board.setRecordSize(pre_trigger_samples, post_trigger_samples)

        # I need to define a "new" recordsPerAcquisition which is an integer
        # number of recordsPerBuffer, otherwise Alazar throws an error
        # We will take care of this below
        records_per_acquisition = records_per_buffer * buffers_per_acquisition

        # Configure the board to make an NPT AutoDMA acquisition
        board.beforeAsyncRead(channels,
                              -pre_trigger_samples,
                              samples_per_record,
                              records_per_buffer,
                              records_per_acquisition,
                              ats.ADMA_EXTERNAL_STARTCAPTURE | ats.ADMA_NPT)

        # Post DMA buffers to board
        for buffer in buffers:
            board.postAsyncBuffer(buffer.addr, buffer.size_bytes)

        board.startCapture()  # Start the acquisition
        buffers_completed = 0

        if not average:
            data = [np.empty((records_per_capture, samples_per_record))
                    for i in range(channel_count)]
        else:
            data = [np.zeros(samples_per_record) for i in range(channel_count)]

        while buffers_completed < buffers_per_acquisition:

            # Wait for the buffer at the head of the list of available
            # buffers to be filled by the board.
            buffer = buffers[buffers_completed % len(buffers)]
            board.waitAsyncBufferComplete(buffer.addr, timeout_ms=15000)
            rbuf = np.reshape(buffer.buffer,
                              (records_per_buffer*channel_count,
                               samples_per_record))
            # making sure we only grab the number of records we asked for
            if buffers_completed < buffers_per_acquisition-1:
                records_to_ignore_val = 0
            else:
                records_to_ignore_val = records_to_ignore

            start = buffers_completed*records_per_buffer
            stop = start + records_per_buffer-records_to_ignore_val
            for i in range(channel_count):
                if average:
                    data[i] += np.sum(rbuf[i*records_per_buffer:
                                           (i+1)*records_per_buffer -
                                           records_to_ignore_val], 0)
                    data[i] /= records_per_capture
                else:
                    data[i][start:stop] = rbuf[i*records_per_buffer:
                                               (i+1)*records_per_buffer -
                                               records_to_ignore_val]

            buffers_completed += 1

            # Add the buffer to the end of the list of available buffers.
            board.postAsyncBuffer(buffer.addr, buffer.size_bytes)

        # Abort transfer.
        board.abortAsyncRead()

        # Check card is not saturated
        maxADC = 2**16-100
        minADC = 100
        if any(np.max(data[i]) > maxADC or np.min(data[i]) < minADC for i in
               range(channel_count)):
            mes = '''Channel A or B are saturated: increase input range or
            decrease amplification'''
            raise InstrIOError(mes)

        # XXX convert to volt

        data_f = []
        for i, c in enumerate(channels_tuple):
            if c:
                if average:
                    data_f.append(np.array(data[i]))
                else:
                    data_f.append(data[i])
            else:
                data_f.append(np.zeros(1))

        return data_f
