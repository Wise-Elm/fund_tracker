#!/usr/bin/python
# -*- coding: utf-8 -*-


import csv
import logging
import uuid
from logging import handlers
from os.path import exists


DEFAULT_DATA_FILE = 'data.csv'
DEFAULT_CORE_LOG_FILENAME = 'storage.log'  # Used when __name__ == '__main__'
CORE_LOG_LEVEL = logging.WARNING
RUNTIME_ID = uuid.uuid4()
CSV_STORAGE_FIELDS = ('symbol', 'name')

# Configure logging.
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class StorageError(RuntimeError):
    """Base class for exceptions arising from this module."""


class Repo:
    """Load and save program data.

    Args:
        load_data (bool): First parameter. Load saved data when true.
        data_file (str or None): Second parameter. When string is given data will be
            saved and loaded to the file represented by the string. When None, data will
            be saved and loaded to defaul file path.
    """

    def __init__(self, load_data: bool, data_file: str):
        self.load_data = load_data
        self.data_file = data_file or DEFAULT_DATA_FILE
        self.symbols_names = []
        self.fields = CSV_STORAGE_FIELDS

        if load_data:
            self.load(self.data_file)

    def save(self, data, data_file):
        """Save application data.

        Must be .csv file type. Saves fund symbol and name if name is populated.

        Args:
            data (list[Fund]): List of Fund objects.
            data_file (str or False): Second parameter. OPTIONAL. String representing a
                file name to save data. '.csv' is the only supported file type. Will
                create new file with that name if one does not exist. If False, will use
                default file name.
        """

        if not data_file:
            data_file = DEFAULT_DATA_FILE

        # Confirm file type is legal.
        if data_file[-4:] != '.csv':
            msg = 'Saving error: data file type must be .csv.'
            log.warning(msg)
            raise StorageError(msg)
        if not exists(data_file):
            self.create_csv(data_file)  # Create file if file not found.
        self.push_to_csv(data, data_file)

    def load(self, data_file):
        """Load application data.

        Args:
            data_file (str or False): String representing a file name from which to
            load data. '.csv' is the only supported file type. Will create new file
            with that name if one does not exist. If False, will use default file name.
        """

        if data_file[-4:] != '.csv':
            msg = 'Loading error: data file type must be .csv.'
            log.warning(msg)
            raise StorageError(msg)
        else:
            self.get_data(data_file)

    def get_data(self, data_file):
        """Check existence of argument file. Loads from file if exists, otherwise
        creates and prepares a new file using argument data_file as file name.

        Args:
            data_file (str or False): String representing a file name from which to
            load data. '.csv' is the only supported file type. Will create new file
            with that name if one does not exist. If False, will use default file name.
        """

        if not exists(data_file):
            self.create_csv(data_file)
        else:
            self.symbols_names = self.get_from_csv(data_file)

    def get_from_csv(self, data_file):
        """Gets data from .csv file specified in argument.

        Args:
            data_file (str or False): String representing a file name from which to
            load data.

        Returns:
            funds (list[list[str(symbol), str(name)]]): List of lists containing fund
                symbols and names as strings.
        """

        funds = []
        with open(data_file, 'r') as csvfile:
            csv_reader = csv.reader(csvfile)
            fields = next(csv_reader)
            for fund in csv_reader:
                funds.append(fund)
        return funds

    def push_to_csv(self, data, data_file):
        """Save data to .csv file specified by argument.

        Args:
            data (list[Fund]): List of Fund objects.
            data_file (str): data_file (str): file name. Must end with '.csv'.
        """

        symbol_name = []  # List[tuples(symbol, name)]

        for fund in data:  # Extract symbol and optional name from Fund.
            symbol_name.append((fund.symbol, fund.name))

        with open(data_file, 'w') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(CSV_STORAGE_FIELDS)
            csv_writer.writerows(symbol_name)

    def create_csv(self, data_file):
        """Create .csv file using argument as file name.

        Args:
            data_file (str): file name. Must end with '.csv'.
        """

        with open(data_file, 'x') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(CSV_STORAGE_FIELDS)
            csv_writer.writerows(self.symbols_names)


def test():
    """For development level module testing."""

    pass


def self_test():
    """Run Unittests on module.

    Args:
        None

    Returns:
        None
    """

    import unittest

    import test_storage

    # Conduct unittest.
    suite = unittest.TestLoader().loadTestsFromModule(test_storage)
    unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == '__main__':

    # Configure Rotating Log. Only runs when module is called directly.
    handler = handlers.RotatingFileHandler(
        filename=DEFAULT_CORE_LOG_FILENAME,
        maxBytes=100**3,
        backupCount=1
    )
    formatter = logging.Formatter(
        f'[%(asctime)s] - {RUNTIME_ID} - %(levelname)s - [%(name)s:%(lineno)s] - '
        f'%(message)s'
    )
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.setLevel(CORE_LOG_LEVEL)

    self_test()