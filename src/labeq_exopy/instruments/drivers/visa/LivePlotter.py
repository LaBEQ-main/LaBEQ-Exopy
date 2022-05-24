# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Authors - Frank Duffy, LaBEQ / Sardashti Research Group, Clemson University
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------

"""Drivers for oxford ips magnet supply using VISA library.

"""
from tracemalloc import reset_peak
from ..driver_tools import (InstrIOError, secure_communication, instrument_property)
from ..visa_tools import VisaInstrument

from matplotlib import pyplot as plt
import numpy as np
import math
import time
from csv import writer

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import time

from csv import writer
from multiprocessing import Process
import os

class LivePlotter(VisaInstrument):
    """Live Plotter

    """
    
    xcol = ""
    ycol = ""
    file = ""
    fname = ""

    def open_connection(self, **para):
        pass

    
    # def __init__(self, *args, **kwargs):
    #     """Open the connection to the instr using the `connection_str`.

    #     """
    #     super(LivePlotter, self).__init__(*args, **kwargs)
        

    def start(self):
        self.fname = (self.file.split("\\")[-1])
        print('plotting',self.xcol,',',self.ycol,'data from: ',self.file)
        fig = plt.figure()
        ani = FuncAnimation(fig, self.animate, interval=500)
        plt.tight_layout()
        plt.show()
    
    def animate(self, i):
    
        data = pd.read_csv(self.file, sep = '\t')
        x = data[self.xcol]
        y = data[self.ycol]

        plt.cla()
        plt.xlabel(str(self.xcol))
        plt.ylabel(str(self.ycol))
        plt.title(f"Live plot: {self.fname}")
        plt.plot(x, y, label=f'Channel {self.fname}')
        plt.legend(loc='upper right')
        plt.tight_layout()