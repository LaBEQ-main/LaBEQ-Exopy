# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------
"""Drivers for oxford ips magnet supply using VISA library.

"""
from ..driver_tools import (InstrIOError, secure_communication)
from ..visa_tools import VisaInstrument

class MercuryiPS(VisaInstrument):
    """Driver for the superconducting magnet power supply MercuryiPS

    """
