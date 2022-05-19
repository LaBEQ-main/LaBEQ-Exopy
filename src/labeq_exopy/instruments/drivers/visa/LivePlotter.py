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

class LivePlotter(VisaInstrument):
    """Driver for the MercuryiPS superconducting magnet power supply 
    manufactured by Oxford Instruments.

    Parameters
    ----------
    see the `VisaInstrument` parameters in the `driver_tools` module

    Methods
    -------
    read_x()
        Return the x quadrature measured by the instrument

    Notes

    -----

    """


    def open_connection(self, **para):
        pass

    
    def __init__(self, *args, **kwargs):
        """Open the connection to the instr using the `connection_str`.

        """
        super(LivePlotter, self).__init__(*args, **kwargs)
        self.y = []
        self.x = []
        
        fig = plt.figure()
        ax = fig.add_axes([0.1,0.1,0.8,0.8])
        plt.ion()
        ax.plot(self.x,self.y, 'b', linestyle='')
        ax.set_title("Data Collection")
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        self.ax = ax
            

    def test(self, x, y):
        
        self.x.append(x)
        self.y.append(y)
        # print(f'x: {self.x}')
        # print(f'y: {self.y}')
        # ti = time.time()
        self.ax.plot(self.x, self.y, color = 'b', marker = 'o', linestyle='')
        # tbp = time.time()
        plt.pause(0.001)
        # tf = time.time()

        # print(f'ti: {ti}, tbp: {tbp}, tf: {tf}')
        # print(f'tbp - ti: {tbp-ti}')
        # print(f'tf-tbp: {tf-tbp}')
        # print(f'tf-ti: {tf-ti}')

        # header = ['tf', 'tbp', 'ti']
        # data = [tf, tbp, ti]
        # with open('C:\\Users\\2administrator\\exopy\\tests\\LivePlottingTest\\data.csv', 'a', newline='') as f_object:
  
        #     # Pass this file object to csv.writer()
        #     # and get a writer object
        #     writer_object = writer(f_object)
        
        #     # Pass the list as an argument into
        #     # the writerow()
        #     writer_object.writerow(data)
        
        #     #Close the file object
        #     f_object.close()

        