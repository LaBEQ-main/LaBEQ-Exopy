# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyHqcLegacy Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Base classes for instrument relying on a custom dll for communication.

"""
import ctypes
import time
from contextlib import contextmanager
from threading import Lock

from .driver_tools import BaseInstrument, InstrIOError


class DllInstrument(BaseInstrument):
    """ A base class for all instrumensts directly calling a dll.

    Attributes
    ----------
    library : str
        Name of the library to use to control this instrument. If is is
        under the instruments/dll directory it will be automatically
        found by the DllForm.

    """

    library = ''


class DllLibrary(object):
    """ Singleton class used to call a dll.

    This class should wrap in python all useful call to the dll, so that the
    driver never need to access the _instance attribute. All manipulation of
    the dll should be done inside the secure context for thread safety.

    Parameters
    ----------
    path : str
        Path to the dll library to load.

    type : {'windll', 'oledll'}, optional
        Calling specification of the dll, by default the cdll one is used.
        (This only makes sense under wind32)

    timeout : float, optional
        Timeout to use when attempting to acquire the library lock.

    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is not None:
            return cls._instance
        else:
            return super(DllLibrary, cls).__new__(cls, *args, **kwargs)

    def __init__(self, path, **kwargs):

        if kwargs.get('type') == 'windll':
            self.dll = ctypes.windll.LoadLibrary(path)
        elif kwargs.get('type') == 'oledll':
            self.dll = ctypes.windll.LoadLibrary(path)
        else:
            self.dll = ctypes.cdll.LoadLibrary(path)

        self.timeout = kwargs.get('timeout', 5.0)

        self.lock = Lock()

    @contextmanager
    def secure(self):
        """ Lock acquire and release method.

        """
        t = 0
        while not self.lock.acquire():
            time.sleep(0.1)
            t += 0.1
            if t > self.timeout:
                raise InstrIOError('Timeout in trying to acquire dll lock.')
        try:
            yield
        finally:
            self.lock.release()
