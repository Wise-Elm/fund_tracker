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
    """Load and save program data."""

    def __init__(self, load_data, data_file):
        self.load_data = load_data
        self.data_file = data_file or DEFAULT_DATA_FILE
        self.symbols_names = []
        self.fields = CSV_STORAGE_FIELDS

        if load_data:
            self.load(self.data_file)

    def save(self, data, data_file):
        if not data_file:
            data_file = DEFAULT_DATA_FILE

        if data_file[-4:] != '.csv':
            msg = 'Saving error: data file type must be .csv.'
            log.warning(msg)
            raise StorageError(msg)
        if not exists(data_file):
            self.create_csv(data_file)
        self.push_to_csv(data, data_file)

    def load(self, data_file):
        if data_file[-4:] != '.csv':
            msg = 'Loading error: data file type must be .csv.'
            log.warning(msg)
            raise StorageError(msg)
        else:
            self.get_data(data_file)

    def get_data(self, data_file):
        if not exists(data_file):
            self.create_csv(data_file)
        else:
            self.symbols_names = self.get_from_csv(data_file)

    def get_from_csv(self, data_file):
        funds = []
        with open(data_file, 'r') as csvfile:
            csv_reader = csv.reader(csvfile)
            fields = next(csv_reader)
            for fund in csv_reader:
                funds.append(fund)
        return funds

    def push_to_csv(self, data, data_file):
        with open(data_file, 'w') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(CSV_STORAGE_FIELDS)
            csv_writer.writerows(self.symbols_names)

    def create_csv(self, data_file):
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