#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Author:
    Graham Steeds

Context:
    This module provides storage functionality.

Description:
    Currently this module provides the functionality to save and load data to .csv
    files, but it is build to be easily expandable to work with other file types.

Expandability:
    To add support for additional file types:

        Step 1:

        Update Repo Instance Attribute self.FILE_TYPES_HANDLERS to include a new key
        and value for the file type and handler method.
            Ex: To include YAML format:
                self.FILE_TYPES_HANDLERS[yaml] = self._yaml_handler

        Add a method to handle requests for the specific file format. The handler
        method will call the saving and loading methods for that file typy and return
        the result from the called method. Ex. for YAML format the naming convention is
        self._yaml_handler. The handler method must take the following arguments:
            Args:
            file_name (str): First parameter. Filename, including extension, for file
                from which to load or save data.
            save_load (string('save' or 'load')): Second parameter. Identifies whether
                to call method to save or load data.
            data (None or list[Fund obj] or list['symbol', 'name']): Third parameter.
                Data on which to perform operations.

            Returns:
            Result from called method.

        Step 2:

        Add a Saving method for file type. Ex: For YAML file type self._save_yaml. The
        saving method must take the following arguments and return the saved data:
            Args:
            data (list[Fund obj] or list['symbol', 'name']): List of fund objects or a
                list of lists containing the symbol and name for each fund.

            Returns:
            data (list[Fund obj] or list['symbol', 'name']): Data that was saved.

        Step 3:

        Add a loading method for the file type. Ex. For YAML file type self._load_yaml.
        The loading method must take the following arguments and return the loaded data.
            Args:
            file_name (str): Filename.

            Returns:
            funds (list[['symbol', 'name']): List of lists containing the symbols and
                names for each saved fund.

Attributes:
    CORE_LOG_LEVEL: Default log level when this module is called directly.
    CSV_STORAGE_FIELDS: Default storage headers for .csv files.
    DEFAULT_FILE_TYPE: Extension for default file type. ex: .csv.
    DEFAULT_FILENAME: Default name for data file.
    DEFAULT_STORAGE_LOG_FILENAME: Default filename for logging when module called
        directly.
    RUNTIME_ID: Generate a unique uuid object. Used in logging.

Composition Attributes:
    Line length = 88 characters.
"""

import csv
import logging
import uuid
from logging import handlers
from os.path import exists

CORE_LOG_LEVEL = logging.WARNING
CSV_STORAGE_FIELDS = ('symbol', 'name')
DEFAULT_FILE_TYPE = '.csv'
DEFAULT_FILENAME = 'data'
DEFAULT_STORAGE_LOG_FILENAME = 'storage.log'  # Used when __name__ == '__main__'
RUNTIME_ID = uuid.uuid4()

# Configure logging.
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class StorageError(RuntimeError):
    """Base class for exceptions arising from this module."""


class Repo:
    """Load and save program data.

    Class level parameters:
        self.FILE_TYPES_HANDLERS: Identify how to handle data file types.

    Args:
        load_data (bool): First parameter. Load saved data when true.
        data_file (str or None): Second parameter. When string is given data will be
            saved and loaded to the file represented by the string. When None, data will
            be saved and loaded to default file path.
    """

    def __init__(self, load_data=True, data_file=None):

        self.FILE_TYPES_HANDLERS = {'csv': self._csv_handler}

        self.load_data = load_data
        self.data_file = data_file
        self.symbols_names = []
        self.fields = CSV_STORAGE_FIELDS

        if load_data:
            self.symbols_names = self.load(self.data_file)

    def load(self, file_name):
        """Load application data.

        Args:
            file_name (str or False): String representing a file name from which to
            load data. '.csv' is the only supported file type. Will create new file
            with that name if one does not exist. If False, will use default file name.
        """

        log.debug(f'Loading from {file_name}...')

        try:
            result = self._file_type_handler(file_name, 'load')
        except StorageError:
            result = []
        except ValueError:
            result = []
        except BaseException:
            result = []
        finally:
            log.debug(f'Length of result: {len(result)}.')
            return result

    def save(self, data, file_name=None):
        """Save application data.

        Args:
            data (list[Fund obj] or list['symbol', 'name']): First parameter. Data to
                be saved.
            file_name (str): Second parameter. File name in which to save data.

        Returns:
            saved_data (list[Fund obj] or list['symbol', 'name']): Data which was saved.
        """

        log.debug(f'Saving data to {file_name}...')

        saved_data = self._file_type_handler(file_name, save_load='save', data=data)

        log.debug(f'Saving data to {file_name} complete.')

        return saved_data

    def _file_type_handler(self, file_name, save_load, data=None):
        """Determines which save and load methods to use.

        Looks at format of file_name argument, determines if the file extension is
        legal, and calls appropriate method. Ex. If file format is .csv, passes
        arguments to methods which handle .csv loading and saving.

        Args:
            file_name (str): First parameter. Filename, including extension, for file
                from which to load or save data.
            save_load (string('save' or 'load')): Second parameter. Identifies whether
                to call method to save or load data.
            data (None or list[Fund obj] or list['symbol', 'name']): Third parameter.
                Data on which to perform operations. Used when data is to be saved.

        Returns:
            result (loaded or saved data): Data on which operation was performed.

        Raises:
            (StorageError): When file_name or save_load arguments are not legal.
        """

        log.debug(f'Handling file type for {file_name}...')

        # Check argument save_load.
        if save_load != 'save' and save_load != 'load':
            msg = f'Argument save_load: {save_load}, is not legal.'
            log.warning(msg)
            raise StorageError(msg)

        # Check to make sure file extension is included.
        if '.' not in file_name:
            msg = 'File name must contain a ({}) proceeded by a legal file ' \
                  'extension.'.format('.')
            raise StorageError(msg)

        # Raise error if file type is not legal.
        if file_name.split('.')[1] not in self.FILE_TYPES_HANDLERS:
            msg = 'File type {} is not a legal type.'.format(file_name.split('.')[1])
            raise StorageError(msg)

        # Identify appropriate handler method based on file type and call method.
        method = self.FILE_TYPES_HANDLERS[file_name.split('.')[1]]
        result = method(file_name, save_load, data)
        return result

    def _csv_handler(self, file_name, save_load, data=None):
        """Determines which csv specific method to call (save or load).

        Args:
            file_name (str): First parameter. Filename, including extension, for file
                from which to load or save data.
            save_load (string('save' or 'load')): Second parameter. Identifies whether
                to call method to save or load data.
            data (None or list[Fund obj] or list['symbol', 'name']): Third parameter.
                Data on which to perform operations. Used when data is to be saved.

        Returns:
            Result from called method.
        """

        log.debug(f'Handling .csv file: {file_name}, action: {save_load}...')

        if save_load == 'save':
            return self._save_csv(data, file_name)

        elif save_load == 'load':
            return self._load_csv(file_name)

    def _load_csv(self, file_name):
        """Load data from .csv file.

        Args:
            file_name (str): Filename.

        Returns:
            funds (list[['symbol', 'name']]): List of lists containing the symbols and
                names for each saved fund.

        Raises:
            StorageError (Exception): when argument file does not exist.
        """

        log.debug(f'Loading from {file_name}...')
        
        if exists(file_name):
            funds = []
            with open(file_name, 'r') as csvfile:
                csv_reader = csv.reader(csvfile)
                fields = next(csv_reader)
                for fund in csv_reader:
                    funds.append(fund)

            log.debug(f'Loading from {file_name} complete.')

            return funds

        else:
            msg = f'File: {file_name}, does not exist. Cannot load from file.'
            log.warning(msg)
            raise StorageError(msg)

    def _save_csv(self, data, file_name):
        """Save data to .csv file.

        Args:
            data (list[Fund obj] or list['symbol', 'name']): List of fund objects or a
                list of lists containing the symbol and name for each fund.

        Returns:
            data (list[Fund obj] or list['symbol', 'name']): Data that was saved.
        """

        log.debug(f'Saving file to {file_name}...')

        # Prepare argument for context manager.
        if exists(file_name):
            log.debug(f'File {file_name} does not yet exist.')
            write_option = 'w'  # w = Open for writing, truncate the file first.
        else:
            log.debug(f'File {file_name} found.')
            write_option = 'x'  # x = Create a new file and open it for writing.

        # Construct list[tuples(symbol, name)].
        try:
            # When data is list[Fund].
            symbol_name = [(fund.symbol, fund.name) for fund in data]

        # When data is list[list['symbol', 'name']].
        except AttributeError:
            symbol_name = [(d[0], d[1]) for d in data]

        log.debug(f'Writing data to {file_name}...')

        # Write data to file.
        with open(file_name, write_option) as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(CSV_STORAGE_FIELDS)
            csv_writer.writerows(symbol_name)

        log.debug(f'Writing data to {file_name} complete.')

        return data


def test():
    """For development level module testing."""

    pass


def storage_self_test():
    """Run Unittests on module.

    Args:
        None

    Returns:
        None
    """

    import unittest

    from tests import test_storage

    # Conduct unittest.
    suite = unittest.TestLoader().loadTestsFromModule(test_storage)
    unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == '__main__':
    # Configure Rotating Log. Only runs when module is called directly.
    handler = handlers.RotatingFileHandler(
        filename=DEFAULT_STORAGE_LOG_FILENAME,
        maxBytes=100**3,  # 0.953674 Megabytes.
        backupCount=1
    )
    formatter = logging.Formatter(
        f'[%(asctime)s] - {RUNTIME_ID} - %(levelname)s - [%(name)s:%(lineno)s] - '
        f'%(message)s'
    )
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.setLevel(CORE_LOG_LEVEL)

    storage_self_test()
