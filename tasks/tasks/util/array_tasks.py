# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyHqcLegacy Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Tasks to operate on numpy.arrays.

"""
import numpy as np
from atom.api import (Enum, Str, set_default)
from exopy.tasks.api import SimpleTask, validators


ARR_VAL = validators.Feval(types=np.ndarray)


class ArrayExtremaTask(SimpleTask):
    """ Store the pair(s) of index/value for the extrema(s) of an array.

    Wait for any parallel operation before execution.

    """
    #: Name of the target in the database.
    target_array = Str().tag(pref=True, feval=ARR_VAL)

    #: Name of the column into which the extrema should be looked for.
    column_name = Str().tag(pref=True)

    #: Flag indicating which extremum shiul be lookd for.
    mode = Enum('Max', 'Min', 'Max & min').tag(pref=True)

    database_entries = set_default({'max_ind': 0, 'max_value': 1.0})

    wait = set_default({'activated': True})  # Wait on all pools by default.

    def perform(self):
        """ Find extrema of database array and store index/value pairs.

        """
        array = self.format_and_eval_string(self.target_array)
        if self.column_name:
            array = array[self.column_name]
        if self.mode == 'Max' or self.mode == 'Max & min':
            ind = np.argmax(array)
            val = array[ind]
            self.write_in_database('max_ind', ind)
            self.write_in_database('max_value', val)
        if self.mode == 'Min' or self.mode == 'Max & min':
            ind = np.argmin(array)
            val = array[ind]
            self.write_in_database('min_ind', ind)
            self.write_in_database('min_value', val)

    def check(self, *args, **kwargs):
        """ Check the target array can be found and has the right column.

        """
        test, traceback = super(ArrayExtremaTask, self).check(*args, **kwargs)

        if not test:
            return test, traceback

        array = self.format_and_eval_string(self.target_array)
        err_path = self.get_error_path()

        if self.column_name:
            if array.dtype.names:
                names = array.dtype.names
                if self.column_name not in names:
                    msg = 'No column named {} in array. (column are : {})'
                    traceback[err_path] = msg.format(self.column_name, names)
                    return False, traceback
            else:
                traceback[err_path] = 'Array has no named columns'
                return False, traceback

        else:
            if array.dtype.names:
                msg = 'The target array has names columns : {}. Choose one'
                traceback[err_path] = msg.format(array.dtype.names)
                return False, traceback
            elif len(array.shape) > 1:
                msg = 'Must use 1d array when using non record arrays.'
                traceback[err_path] = msg
                return False, traceback

        return test, traceback

    def _post_setattr_mode(self, old, new):
        """ Update the database entries according to the mode.

        """
        if new == 'Max':
            self.database_entries = {'max_ind': 0, 'max_value': 2.0}
        elif new == 'Min':
            self.database_entries = {'min_ind': 0, 'min_value': 1.0}
        else:
            self.database_entries = {'max_ind': 0, 'max_value': 2.0,
                                     'min_ind': 0, 'min_value': 1.0}


class ArrayFindValueTask(SimpleTask):
    """ Store the index of the first occurence of a value in an array.

    Wait for any parallel operation before execution.

    """
    #: Name of the target in the database.
    target_array = Str().tag(pref=True, feval=ARR_VAL)

    #: Name of the column into which the extrema should be looked for.
    column_name = Str().tag(pref=True)

    #: Value which should be looked for in the array.
    value = Str().tag(pref=True, feval=validators.Feval())

    database_entries = set_default({'index': 0})

    wait = set_default({'activated': True})  # Wait on all pools by default.

    def perform(self):
        """ Find index of value array and store index in database.

        """
        array = self.format_and_eval_string(self.target_array)
        if self.column_name:
            array = array[self.column_name]

        val = self.format_and_eval_string(self.value)

        try:
            ind = np.where(np.abs(array - val) < 1e-12)[0][0]
        except IndexError as e:
            msg = 'Could not find {} in array {} ({})'
            raise ValueError(msg.format(val, self.target_array, array)) from e
        self.write_in_database('index', ind)

    def check(self, *args, **kwargs):
        """ Check the target array can be found and has the right column.

        """
        test, traceback = super(ArrayFindValueTask, self).check(*args,
                                                                **kwargs)

        if not test:
            return test, traceback

        err_path = self.get_error_path()

        array = self.format_and_eval_string(self.target_array)

        if self.column_name:
            if array.dtype.names:
                names = array.dtype.names
                if self.column_name not in names:
                    msg = 'No column named {} in array. (column are : {})'
                    traceback[err_path] = msg.format(self.column_name, names)
                    return False, traceback
            else:
                traceback[err_path] = 'Array has no named columns'
                return False, traceback

        else:
            if array.dtype.names:
                msg = 'The target array has names columns : {}. Choose one'
                traceback[err_path] = msg.format(array.dtype.names)
                return False, traceback
            elif len(array.shape) > 1:
                msg = 'Must use 1d array when using non record arrays.'
                traceback[err_path] = msg
                return False, traceback

        return test, traceback
