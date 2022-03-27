# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2020 by ExopyHqcLegacy Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Interface allowing to use RF tasks with Anapico multi-channel generator.

"""
from atom.api import Int

from exopy.tasks.api import TaskInterface


class AnapicoSetChannelInterface(TaskInterface):
    """Set the central frequency to be used for the specified channel.

    """
    #: Id of the channel whose central frequency should be set.
    channel = Int(1).tag(pref=True)

    def perform(self, frequency=None):
        """Set the central frequency of the specified channel.

        """
        task = self.task
        channel = self.channel
        task.driver.channel = channel
        task.i_perform()
