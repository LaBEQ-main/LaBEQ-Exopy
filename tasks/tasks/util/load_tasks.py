# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyHqcLegacy Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Tasks to used to load a file in memory.

"""
import os

import numpy as np
import h5py
from atom.api import (Bool, Str, List, set_default)
from past.builtins import basestring

from exopy.tasks.api import SimpleTask, InterfaceableTaskMixin, TaskInterface


def _make_array(names, dtypes='f8'):
    if isinstance(dtypes, basestring):
        dtypes = [dtypes for i in range(len(names))]

    dtype = {'names': names, 'formats': dtypes}
    return np.ones((5,), dtype=dtype)


class LoadArrayTask(InterfaceableTaskMixin, SimpleTask):
    """ Load an array from the disc into the database.

    """
    #: Folder from which to load the data.
    folder = Str().tag(pref=True, fmt=True)

    #: Name of the file from which to load the data.
    filename = Str().tag(pref=True, fmt=True)

    #: Kind of file to load.
    selected_format = Str().tag(pref=True)

    database_entries = set_default({'array': _make_array(['var1', 'var2'])})

    def check(self, *args, **kwargs):
        """Check that the provided path and filename make sense.

        """
        test, traceback = super(LoadArrayTask, self).check(*args, **kwargs)
        err_path = self.get_error_path()

        if not test:
            return test, traceback

        full_folder_path = self.format_string(self.folder)
        filename = self.format_string(self.filename)
        full_path = os.path.join(full_folder_path, filename)

        if not os.path.isfile(full_path):
            msg = ('File does not exist, be sure that your measure  will '
                   'create it before this task is executed.')
            traceback[err_path + '-file'] = msg

        return test, traceback


class CSVLoadInterface(TaskInterface):
    """Interface used to load CSV files.

    """
    #: Delimiter used in the file to load.
    delimiter = Str('\t').tag(pref=True)

    #: Character used to signal a comment.
    comments = Str('#').tag(pref=True)

    #: Flag indicating whether or not to use the first row as column names.
    names = Bool(True).tag(pref=True)

    #: The users can provide the names which will be available in its file
    #: if the file cannot be found when checks are run.
    c_names = List(Str()).tag(pref=True)

    #: Class attr used in the UI.
    file_formats = ['CSV']

    def perform(self):
        """Load a file stored in csv format.

        """
        task = self.task
        folder = task.format_string(task.folder)
        filename = task.format_string(task.filename)
        full_path = os.path.join(folder, filename)

        comment_lines = 0
        with open(full_path) as f:
            while True:
                if f.readline().startswith(self.comments):
                    comment_lines += 1
                else:
                    break

        data = np.genfromtxt(full_path, comments=self.comments,
                             delimiter=self.delimiter, names=self.names,
                             skip_header=comment_lines)

        task.write_in_database('array', data)

    def check(self, *args, **kwargs):
        """Try to find the names of the columns to add the array in the
        database.

        """
        task = self.task
        if self.c_names:
            return True, {}

        try:
            full_folder_path = task.format_string(task.folder)
            filename = task.format_string(task.filename)
        except Exception:
            return True, {}

        full_path = os.path.join(full_folder_path, filename)

        if os.path.isfile(full_path):
            with open(full_path) as f:
                while True:
                    line = f.readline()
                    if not line.startswith(self.comments):
                        names = line.split(self.delimiter)
                        names = [n.strip() for n in names if n]
                        self.task.write_in_database('array',
                                                    _make_array(names))
                        break

        return True, {}

    def _post_setattr_c_names(self, old, new):
        """Keep the c_names  in sync with the array in the database.

        """
        if new:
            self.task.write_in_database('array', _make_array(new))


class H5PYLoadInterface(TaskInterface):
    """Interface used to load .h5 files.

    The task supports the Single Writter Multiple
    Readers mode which allows read-only access while the file is still
    being written by another  task without any race conditions.

    """
    #: Class attr used in the UI.
    file_formats = ['H5PY']

    #: Whether or not the HDF5 file supports SWMR
    swmr = Bool(True).tag(pref=True)

    def perform(self):
        """Load a file stored in h5py format.

        Can also handle a file currently opened by a SaveFileHDF5Task.
        For more reliability, both tasks should use the SWMR mode.
        """
        task = self.task
        folder = task.format_string(task.folder)
        filename = task.format_string(task.filename)
        full_path = os.path.join(folder, filename)

        with h5py.File(full_path,'r', swmr=self.swmr) as f:
            data_dict = {}
            # If the file is still opened by a saveFileHDF5Task,
            # we need to truncate the data
            if 'count_calls' in f.attrs:
                count_calls = f.attrs['count_calls']
                for key in f:
                    data_dict[key] = np.array(f[key][:count_calls])

        task.write_in_database('array', data_dict)

    def check(self, *args, **kwargs):
        """Try to find the names of the keys

        """
        try:
            full_folder_path = task.format_string(task.folder)
            filename = task.format_string(task.filename)
        except Exception:
            return True, {}

        full_path = os.path.join(full_folder_path, filename)

        if os.path.isfile(full_path):
            with h5py.File(full_path,'r', swmr=self.swmr) as f:
                self.task.write_in_database('array',
                                            {k: np.ones(5) for k in f})

        return True, {}
