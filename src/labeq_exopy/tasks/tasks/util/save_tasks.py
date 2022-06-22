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
import errno
import logging
import numbers
import warnings
from inspect import cleandoc
from collections import OrderedDict

#: Protection against numpy deprecation message in h5py
warnings.filterwarnings("ignore", category=FutureWarning, module="h5py")

import numpy
import h5py
from atom.api import Enum, Value, Bool, Int, Typed, List, set_default, Str

from exopy.tasks.api import SimpleTask, validators
from exopy.utils.atom_util import ordered_dict_from_pref, ordered_dict_to_pref
from exopy.utils.traceback import format_exc


class SaveTask(SimpleTask):
    """ Save the specified entries either in a CSV file or an array. The file
    is closed when the line number is reached.

    Wait for any parallel operation before execution.

    Notes
    -----
    Currently only support saving floats.

    """
    #: Kind of object in which to save the data.
    saving_target = Enum('File', 'Array', 'File and array').tag(pref=True)

    #: Folder in which to save the data.
    folder = Str('{default_path}').tag(pref=True)

    #: Name of the file in which to write the data.
    filename = Str().tag(pref=True)

    #: Currently opened file object. (File mode)
    file_object = Value()

    #: Opening mode to use when saving to a file.
    file_mode = Enum('Add', 'New').tag(pref=True)

    #: Header to write at the top of the file.
    header = Str().tag(pref=True)

    #: Numpy array in which data are stored (Array mode)
    array = Value()  # Array

    #: Size of the data to be saved. (Evaluated at runtime)
    array_size = Str().tag(pref=True)

    #: Computed size of the data (post evaluation)
    array_length = Int()

    #: Index of the current line.
    line_index = Int(0)

    #: Values to save as an ordered dictionary.
    saved_values = Typed(OrderedDict, ()).tag(pref=(ordered_dict_to_pref,
                                                    ordered_dict_from_pref))

    #: Flag indicating whether or not initialisation has been performed.
    initialized = Bool(False)

    wait = set_default({'activated': True})  # Wait on all pools by default.

    def perform(self):
        """ Collect all data and write them to array or file according to mode.

        On first call initialise the system by opening file and/or array. Close
        file when the expected number of lines has been written.

        """
        print(f'self.file_mode1: {self.file_mode}')
        # Initialisation.
        if not self.initialized:

            self.line_index = 0
            size_str = self.array_size
            if size_str:
                self.array_length = self.format_and_eval_string(size_str)
            else:
                self.array_length = -1

            if self.saving_target != 'Array':
                full_folder_path = self.format_string(self.folder)
                filename = self.format_string(self.filename)
                full_path = os.path.join(full_folder_path, filename)
                mode = 'wb' if self.file_mode == 'New' else 'ab'

                print(f'self.file_mode2: {self.file_mode}')
                print(f'mode: {mode}')

                try:
                    self.file_object = open(full_path, mode)
                except IOError as e:
                    log = logging.getLogger()
                    mes = ('In {}, failed to open the specified '
                           'file {}').format(self.name, e)
                    log.error(mes)
                    self.root.should_stop.set()

                self.root.resources['files'][full_path] = self.file_object
                if self.header:
                    h = self.format_string(self.header)
                    for line in h.split('\n'):
                        self.file_object.write(('# ' + line +
                                                '\n').encode('utf-8'))
                labels = [self.format_string(s) for s in self.saved_values]
                self.file_object.write(('\t'.join(labels) +
                                        '\n').encode('utf-8'))
                self.file_object.flush()

            if self.saving_target != 'File':
                # TODO add more flexibilty on the dtype (possible complex
                # values)
                dtype = numpy.dtype({'names': [self.format_string(s)
                                               for s in self.saved_values],
                                     'formats': ['f8']*len(self.saved_values)})
                self.array = numpy.empty((self.array_length,),
                                         dtype=dtype)
                self.write_in_database('array', self.array)
            self.initialized = True

        # Writing
        values = tuple(self.format_and_eval_string(s)
                       for s in self.saved_values.values())
        if self.saving_target != 'Array':
            new_line = '\t'.join([str(val) for val in values]) + '\n'
            self.file_object.write(new_line.encode('utf-8'))
            self.file_object.flush()
        if self.saving_target != 'File':
            self.array[self.line_index] = tuple(values)

        self.line_index += 1

        # Closing
        if self.line_index == self.array_length:
            if self.file_object:
                self.file_object.close()
            self.initialized = False

    def check(self, *args, **kwargs):
        """Check that the provided parameters make sense.

        """
        err_path = self.get_error_path()
        test, traceback = super(SaveTask, self).check(*args, **kwargs)

        if self.saving_target != 'Array':
            try:
                full_folder_path = self.format_string(self.folder)
            except Exception as e:
                mess = 'Failed to format the folder path: {}'
                traceback[err_path] = mess.format(e)
                return False, traceback

            try:
                filename = self.format_string(self.filename)
            except Exception as e:
                mess = 'Failed to format the filename: {}'
                traceback[err_path] = mess.format(e)
                return False, traceback

            full_path = os.path.join(full_folder_path, filename)

            overwrite = False
            if self.file_mode == 'New' and os.path.isfile(full_path):
                overwrite = True
                traceback[err_path + '-file'] = \
                    ('File already exists, running the measure will '
                     'override it.')

            try:
                f = open(full_path, 'ab')
                f.close()
                if self.file_mode == 'New' and not overwrite:
                    os.remove(full_path)
            except Exception as e:
                mess = 'Failed to open the specified file : {}'.format(e)
                traceback[err_path] = mess.format(e)
                return False, traceback

            try:
                self.format_string(self.header)
            except Exception as e:
                mess = 'Failed to format the header: {}'
                traceback[err_path] = mess.format(e)
                return False, traceback

        if self.array_size:
            try:
                self.format_and_eval_string(self.array_size)
            except Exception as e:
                mess = 'Failed to compute the array size: {}'
                traceback[err_path] = mess.format(e)
                return False, traceback

        elif self.saving_target != 'File':
            traceback[err_path] = 'A size for the array must be provided.'
            return False, traceback

        labels = list()
        for i, (l, v) in enumerate(self.saved_values.items()):
            try:
                labels.append(self.format_string(l))
            except Exception:
                traceback[err_path + '-label_' + str(i)] = \
                    'Failed to evaluate label {}:\n{}'.format(l, format_exc())
                test = False
            try:
                self.format_and_eval_string(v)
            except Exception:
                traceback[err_path + '-entry_' + str(i)] = \
                    'Failed to evaluate entry {}:\n{}'.format(v, format_exc())
                test = False

        if not test:
            return test, traceback

        if len(set(labels)) != len(self.saved_values):
            traceback[err_path] = "All labels must be different."
            return False, traceback

        if self.saving_target != 'File':
            data = [numpy.array([0.0, 1.0]) for s in self.saved_values]
            names = str(','.join([s for s in labels]))
            final_arr = numpy.rec.fromarrays(data, names=names)

            self.write_in_database('array', final_arr)

        return test, traceback

    def _post_setattr_saving_target(self, old, new):
        """Add the array in the database if using it.

        """
        if new != 'File':
            self.database_entries = {'array': numpy.array([1.0])}
        else:
            self.database_entries = {}


class SaveFileTask(SimpleTask):
    """ Save the specified entries in a CSV file.

    Wait for any parallel operation before execution.

    Notes
    -----
    Currently only support saving floats and arrays of floats (record arrays
    or simple arrays).

    """
    #: Folder in which to save the data.
    folder = Str('{default_path}').tag(pref=True, fmt=True)

    #: Name of the file in which to write the data.
    filename = Str().tag(pref=True, fmt=True)

    #: Currently opened file object. (File mode)
    file_object = Value()

    #: Header to write at the top of the file.
    header = Str().tag(pref=True, fmt=True)

    #: Values to save as an ordered dictionary.
    saved_values = Typed(OrderedDict, ()).tag(pref=(ordered_dict_to_pref,
                                                    ordered_dict_from_pref))

    #: Flag indicating whether or not initialisation has been performed.
    initialized = Bool(False)

    #: Column indices identified as arrays. Use to save 2D arrays in
    #: concatenated columns.
    array_values = Value()

    #: Shapes of identified arrays.
    array_dims = Value()

    database_entries = set_default({'file': None})

    wait = set_default({'activated': True})  # Wait on all pools by default.

    def perform(self):
        """ Collect all data and write them to file.

        """
        # Initialisation.
        if not self.initialized:

            full_folder_path = self.format_string(self.folder)
            filename = self.format_string(self.filename)
            full_path = os.path.join(full_folder_path, filename)
            try:
                self.file_object = open(full_path, 'wb')
            except IOError:
                log = logging.getLogger()
                msg = "In {}, failed to open the specified file."
                log.exception(msg.format(self.name))
                self.root.should_stop.set()

            self.root.resources['files'][full_path] = self.file_object

            if self.header:
                h = self.format_string(self.header)
                for line in h.split('\n'):
                    self.file_object.write(('# ' + line +
                                            '\n').encode('utf-8'))

            labels = []
            self.array_values = list()
            self.array_dims = list()
            for i, (l, v) in enumerate(self.saved_values.items()):
                label = self.format_string(l)
                value = self.format_and_eval_string(v)
                if isinstance(value, numpy.ndarray):
                    names = value.dtype.names
                    self.array_values.append(i)
                    self.array_dims.append(value.ndim)
                    if names:
                        labels.extend([label + '_' + m for m in names])
                    else:
                        labels.append(label)
                else:
                    labels.append(label)
            self.file_object.write(('\t'.join(labels) + '\n').encode('utf-8'))
            self.file_object.flush()

            self.initialized = True

        shapes_1D = set()
        shapes_2D = set()
        values = []
        for i, v in enumerate(self.saved_values.values()):
            value = self.format_and_eval_string(v)
            values.append(value)
            if i in self.array_values:  # if we deal with an array_type value
                if len(value.shape) == 1:
                    shapes_1D.add(value.shape)
                elif len(value.shape) == 2:
                    shapes_2D.add(value.shape)
                else:
                    log = logging.getLogger()
                    msg = ("In {}, impossible to save arrays exceeding two "
                           "dimension. Save file in HDF5 format.")
                    log.error(msg.format(self.name))
                    self.root.should_stop.set()

        if shapes_1D:
            if len(shapes_1D) > 1:
                log = logging.getLogger()
                msg = ("In {}, impossible to save simultaneously 1D-arrays of "
                       "different sizes. Save file in HDF5 format.")
                log.error(msg.format(self.name))
                self.root.should_stop.set()
            else:
                length = shapes_1D.pop()

        if shapes_2D:
            if len(shapes_2D) > 1:
                log = logging.getLogger()
                msg = ("In {}, impossible to save simultaneously 2D-arrays of "
                       "different sizes. Save file in HDF5 format.")
                log.error(msg.format(self.name))
                self.root.should_stop.set()
            elif shapes_1D:
                if length == shapes_2D[0]:
                    shape = shapes_2D.pop()
                else:
                    log = logging.getLogger()
                    msg = ("In {}, 1D-arrays and 2D-arrays could not be "
                           "broadcast together. Save file in HDF5 format.")
                    log.error(msg.format(self.name))
                    self.root.should_stop.set()
            else:
                shape = shapes_2D.pop()

        if not self.array_values:
            new_line = '\t'.join([str(val) for val in values]) + '\n'
            self.file_object.write(new_line.encode('utf-8'))
            self.file_object.flush()
        else:
            columns = []
            if not (2 in self.array_dims):
                for i, val in enumerate(values):
                    if i in self.array_values:
                        if val.dtype.names:
                            columns.extend([val[m] for m in val.dtype.names])
                        else:
                            columns.append(val)
                    else:
                        columns.append(numpy.ones(length)*val)
            else:
                for i, val in enumerate(values):
                    if i in self.array_values:
                        if val.ndim == 1:
                            val_2D = numpy.array([val]).T
                            ones = numpy.ones((1, shape[1]))
                            val = numpy.multiply(val_2D, ones)
                    else:
                        val = numpy.ones(shape[0]*shape[1])*val
                    columns.append(val.reshape((shape[0]*shape[1])))
            array_to_save = numpy.rec.fromarrays(columns)
            numpy.savetxt(self.file_object, array_to_save, delimiter='\t')
            self.file_object.flush()

    def check(self, *args, **kwargs):
        """Check that given parameters are meaningful

        """
        err_path = self.get_error_path()
        test, traceback = super(SaveFileTask, self).check(*args, **kwargs)
        try:
            full_folder_path = self.format_string(self.folder)
            filename = self.format_string(self.filename)
        except Exception:
            return test, traceback

        full_path = os.path.join(full_folder_path, filename)

        overwrite = False
        if os.path.isfile(full_path):
            overwrite = True
            traceback[err_path + '-file'] = \
                cleandoc('''File already exists, running the measure will
                override it.''')

        try:
            f = open(full_path, 'ab')
            f.close()
            if not overwrite:
                os.remove(full_path)
        except Exception as e:
            mess = 'Failed to open the specified file : {}'.format(e)
            traceback[err_path] = mess.format(e)
            return False, traceback

        labels = set()
        for i, (l, v) in enumerate(self.saved_values.items()):
            try:
                labels.add(self.format_string(l))
            except Exception:
                traceback[err_path + '-label_' + str(i)] = \
                    'Failed to evaluate label {}:\n{}'.format(l, format_exc())
                test = False
            try:
                self.format_and_eval_string(v)
            except Exception:
                traceback[err_path + '-entry_' + str(i)] = \
                    'Failed to evaluate entry {}:\n{}'.format(v, format_exc())
                test = False

        if not test:
            return test, traceback

        if len(labels) != len(self.saved_values):
            traceback[err_path] = "All labels must be different."
            return False, traceback

        return test, traceback


class _HDF5File(h5py.File):
    """Resize the datasets before closing the file

    Sets the compression with a boolean

    """

    def close(self):
        for dataset in self.keys():
            oldshape = self[dataset].shape
            newshape = (self.attrs['count_calls'], ) + oldshape[1:]
            self[dataset].resize(newshape)
        super(_HDF5File, self).close()

    def create_dataset(self, name, shape, maximumshape, datatype, compress):
        f = super(_HDF5File, self)
        if compress != 'None':
            f.create_dataset(name, shape, maxshape=maximumshape,
                             dtype=datatype, compression=compress)
        else:
            f.create_dataset(name, shape, maxshape=maximumshape,
                             dtype=datatype)

VAL_REAL = validators.Feval(types=numbers.Real)


class SaveFileHDF5Task(SimpleTask):
    """ Save the specified entries in a HDF5 file.

    Wait for any parallel operation before execution.

    """
    #: Folder in which to save the data.
    folder = Str('{default_path}').tag(pref=True, fmt=True)

    #: Name of the file in which to write the data.
    filename = Str().tag(pref=True, fmt=True)

    #: Currently opened file object. (File mode)
    file_object = Value()

    #: Header to write at the top of the file.
    header = Str().tag(pref=True, fmt=True)

    #: Values to save as an ordered dictionary.
    saved_values = Typed(OrderedDict, ()).tag(pref=(ordered_dict_to_pref,
                                                    ordered_dict_from_pref))

    #: Data type (float16, float32, etc.)
    datatype = Enum('float16', 'float32', 'float64').tag(pref=True)

    #: Compression type of the data in the HDF5 file
    compression = Enum('None', 'gzip').tag(pref=True)

    #: Estimation of the number of calls of this task during the measure.
    #: This helps h5py to chunk the file appropriately
    calls_estimation = Str('1').tag(pref=True, feval=VAL_REAL)

    #: Flag indicating whether or not the data should be saved in swmr mode
    swmr = Bool(True).tag(pref=True)

    #: Flag indicating whether or not initialisation has been performed.
    initialized = Bool(False)

    database_entries = set_default({'file': None})

    wait = set_default({'activated': True})  # Wait on all pools by default.

    def perform(self):
        """ Collect all data and write them to file.

        """

        calls_estimation = self.format_and_eval_string(self.calls_estimation)

        # Initialisation.
        if not self.initialized:

            self._formatted_labels = []
            full_folder_path = self.format_string(self.folder)
            filename = self.format_string(self.filename)
            full_path = os.path.join(full_folder_path, filename)
            try:
                if self.swmr:
                    # Not backwards compatible
                    self.file_object = _HDF5File(full_path, 'w', libver='latest')
                else:
                    self.file_object = _HDF5File(full_path, 'w')
            except IOError:
                log = logging.getLogger()
                msg = "In {}, failed to open the specified file."
                log.exception(msg.format(self.name))
                self.root.should_stop.set()

            self.root.resources['files'][full_path] = self.file_object

            f = self.file_object
            for l, v in self.saved_values.items():
                label = self.format_string(l)
                self._formatted_labels.append(label)
                value = self.format_and_eval_string(v)
                if isinstance(value, numpy.ndarray):
                    names = value.dtype.names
                    if names:
                        for m in names:
                            f.create_dataset(label + '_' + m,
                                             (calls_estimation,) + value[m].shape,
                                             (None, ) + value[m].shape,
                                             self.datatype,
                                             self.compression)
                    else:
                        f.create_dataset(label,
                                         (calls_estimation,) + value.shape,
                                         (None, ) + value.shape,
                                         self.datatype,
                                         self.compression)
                else:
                    f.create_dataset(label, (calls_estimation,), (None,),
                                     self.datatype, self.compression)
            f.attrs['header'] = self.format_string(self.header)
            f.attrs['count_calls'] = 0
            if self.swmr:
                f.swmr_mode = True
            f.flush()

            self.initialized = True

        f = self.file_object
        count_calls = f.attrs['count_calls']

        if not (count_calls % calls_estimation):
            for dataset in f.keys():
                oldshape = f[dataset].shape
                newshape = (oldshape[0] + calls_estimation, ) + oldshape[1:]
                f[dataset].resize(newshape)

        labels = self._formatted_labels
        for i, v in enumerate(self.saved_values.values()):
            value = self.format_and_eval_string(v)
            if isinstance(value, numpy.ndarray):
                names = value.dtype.names
                if names:
                    for m in names:
                        f[labels[i] + '_' + m][count_calls] = value[m]
                else:
                    f[labels[i]][count_calls] = value
            else:
                f[labels[i]][count_calls] = value

        f.attrs['count_calls'] = count_calls + 1
        f.flush()

    def check(self, *args, **kwargs):
        """Check that all the parameters are correct.

        """
        err_path = self.get_error_path()
        test, traceback = super(SaveFileHDF5Task, self).check(*args, **kwargs)
        try:
            full_folder_path = self.format_string(self.folder)
            filename = self.format_string(self.filename)
        except Exception:
            return test, traceback

        full_path = os.path.join(full_folder_path, filename)

        overwrite = False
        if os.path.isfile(full_path):
            overwrite = True
            traceback[err_path + '-file'] = \
                cleandoc('''File already exists, running the measure will
                override it.''')

        try:
            f = open(full_path, 'ab')
            f.close()
            if not overwrite:
                os.remove(full_path)
        except Exception as e:
            mess = 'Failed to open the specified file : {}'.format(e)
            traceback[err_path] = mess.format(e)
            return False, traceback

        labels = set()
        for i, (l, v) in enumerate(self.saved_values.items()):
            try:
                labels.add(self.format_string(l))
            except Exception:
                traceback[err_path + '-label_' + str(i)] = \
                    'Failed to evaluate label {}:\n{}'.format(l, format_exc())
                test = False
            try:
                self.format_and_eval_string(v)
            except Exception:
                traceback[err_path + '-entry_' + str(i)] = \
                    'Failed to evaluate entry {}:\n{}'.format(v, format_exc())
                test = False

        if not test:
            return test, traceback

        if len(labels) != len(self.saved_values):
            traceback[err_path] = "All labels must be different."
            return False, traceback

        return test, traceback

    #: List of the formatted names of the entries.
    _formatted_labels = List()


ARR_VAL = validators.Feval(types=numpy.ndarray)


class SaveArrayTask(SimpleTask):
    """Save the specified array either in a CSV file or as a .npy binary file.

    Wait for any parallel operation before execution.

    """

    #: Folder in which to save the data.
    folder = Str().tag(pref=True, fmt=True)

    #: Name of the file in which to write the data.
    filename = Str().tag(pref=True, fmt=True)

    #: Header to write at the top of the file.
    header = Str().tag(pref=True, fmt=True)

    #: Name of the array to save in the database.
    target_array = Str().tag(pref=True, feval=ARR_VAL)

    #: Flag indicating whether to save as csv or .npy.
    mode = Enum('Text file', 'Binary file').tag(pref=True)

    wait = set_default({'activated': True})  # Wait on all pools by default.

    def perform(self):
        """ Save array to file.

        """
        array_to_save = self.format_and_eval_string(self.target_array)

        assert isinstance(array_to_save, numpy.ndarray), 'Wrong type returned.'

        full_folder_path = self.format_string(self.folder)

        filename = self.format_string(self.filename)

        full_path = os.path.join(full_folder_path, filename)

        # Create folder if it does not exists.
        try:
            os.makedirs(full_folder_path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

        if self.mode == 'Text file':
            try:
                file_object = open(full_path, 'wb')
            except IOError:
                msg = "In {}, failed to open the specified file"
                log = logging.getLogger()
                log.exception(msg.format(self.name))
                raise

            if self.header:
                h = self.format_string(self.header)
                for line in h.split('\n'):
                    file_object.write(('# ' + line + '\n').encode('utf-8'))

            if array_to_save.dtype.names:
                names = '\t'.join(array_to_save.dtype.names) + '\n'
                file_object.write(names.encode('utf-8'))

            numpy.savetxt(file_object, array_to_save, delimiter='\t')
            file_object.close()

        else:
            try:
                file_object = open(full_path, 'wb')
                file_object.close()
            except IOError:
                msg = "In {}, failed to open the specified file."
                log = logging.getLogger()
                log.exception(msg.format(self.name))

                self.root.should_stop.set()
                return

            numpy.save(full_path, array_to_save)

    def check(self, *args, **kwargs):
        """Check folder path and filename.

        """
        err_path = self.get_error_path()
        test, traceback = super(SaveArrayTask, self).check(*args, **kwargs)

        if self.mode == 'Binary file':
            if len(self.filename) > 3 and self.filename[-4] == '.'\
                    and self.filename[-3:] != 'npy':
                self.filename = self.filename[:-4] + '.npy'
                msg = ("The extension of the file will be replaced by '.npy' "
                       "in task {}").format(self.name)
                traceback[err_path + '-file_ext'] = msg

            if self.header:
                traceback[err_path + '-header'] =\
                    'Cannot write a header when saving in binary mode.'

        try:
            full_folder_path = self.format_string(self.folder)
            filename = self.format_string(self.filename)
        except Exception:
            return test, traceback

        full_path = os.path.join(full_folder_path, filename)

        overwrite = False
        if os.path.isfile(full_path):
            overwrite = True
            traceback[err_path + '-file'] = \
                cleandoc('''File already exists, running the measure will
                override it.''')

        try:
            f = open(full_path, 'ab')
            f.close()
            if not overwrite:
                os.remove(full_path)
        except Exception as e:
            mess = 'Failed to open the specified file: {}'
            traceback[err_path] = mess.format(e)
            return False, traceback

        return test, traceback
