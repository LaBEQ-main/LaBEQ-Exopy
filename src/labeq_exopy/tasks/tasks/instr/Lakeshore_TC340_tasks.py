# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Authors - Kathryn Evancho, LaBEQ / Sardashti Research Group, Clemson University
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------

"""Task 

"""

from atom.api import (Enum, Bool)
from exopy.tasks.api import InstrumentTask

class LakeshoreTC340MeasureTask(InstrumentTask):
    
    def perform(self):
        ''
class LakeshoreTC340ConfigureTask(InstrumentTask):
    
    def perform(self):
        ''