#!/usr/bin/python
# -*- coding: utf-8 -*-

"""This module is used to test storage.py."""
import os
import unittest

from storage import Repo, StorageError
from test_assets import ASSETS


DEFAULT_STORAGE_TEST_FILENAME = 'test_storage.csv'


class TestApplication(unittest.TestCase):
    """Test storage.py."""

    @classmethod
    def setUpClass(cls):
        """Create a test file."""

        repo = Repo(load_data=False)
        repo.save(ASSETS, DEFAULT_STORAGE_TEST_FILENAME)

    @classmethod
    def tearDownClass(cls):
        """Delete test file."""

        os.remove(DEFAULT_STORAGE_TEST_FILENAME)

    def setUp(self):
        """Load test file data."""

        self.repo = Repo(data_file=DEFAULT_STORAGE_TEST_FILENAME)

    def tearDown(self):
        pass

    def test_functions(self):
        pass

    def test_load(self):
        """Test load."""

        # Confirm that data loaded is the same as the data before it was saved.
        self.assertEqual(ASSETS, self.repo.load(DEFAULT_STORAGE_TEST_FILENAME))

        # Confirm blank list is return from a bad filename.
        self.assertEqual(self.repo.load('bad_filename.csv'), [])

    def test_file_type_handler(self):
        """Test file_type_handler."""

        # Confirm error is raised when using a bad file type.
        self.assertRaises(
            StorageError,
            self.repo._file_type_handler,
            'bad_filename.abc',
            'load'
        )

        # Confirm error is raised when using a bad argument; save_load = 'asdf'.
        self.assertRaises(
            StorageError,
            self.repo._file_type_handler,
            DEFAULT_STORAGE_TEST_FILENAME,
            'asdf'
        )

    def test_save_csv_and_load_csv(self):
        """Test _save_csv and _load_csv methods."""

        # Save test data to DEFAULT_STORAGE_TEST_FILENAME.
        self.repo._save_csv(ASSETS, DEFAULT_STORAGE_TEST_FILENAME)

        # Load information from DEFAULT_STORAGE_TEST_FILENAME.
        loaded_data = self.repo._load_csv(DEFAULT_STORAGE_TEST_FILENAME)

        # Confirm that test data is the same through a saving and loading cycle.
        self.assertEqual(loaded_data, ASSETS)


if __name__ == '__main__':
    unittest.main()
