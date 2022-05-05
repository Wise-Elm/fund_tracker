#!/usr/bin/python
# -*- coding: utf-8 -*-

"""This module is used to test storage.py."""
import os
import unittest

# External Imports
from storage import Repo, StorageError
from tests.test_assets import SYMBOL_NAME


DEFAULT_STORAGE_TEST_FILENAME = 'test_storage.csv'


class TestApplication(unittest.TestCase):
    """Test storage.py."""

    @classmethod
    def setUpClass(cls):
        """Create a test file."""

        # Initialize and instantiate Repo in test mode, with test data.
        repo = Repo(load_data=False)
        repo.save(SYMBOL_NAME, DEFAULT_STORAGE_TEST_FILENAME)

    @classmethod
    def tearDownClass(cls):
        """Delete test file."""

        # Delete test file once testing is complete.
        os.remove(DEFAULT_STORAGE_TEST_FILENAME)

    def setUp(self):
        """Load test file data."""

        # Reload test data for each test.
        self.repo = Repo(data_file=DEFAULT_STORAGE_TEST_FILENAME)

    def tearDown(self):
        pass

    def test_functions(self):
        pass

    def test_load(self):
        """Test load."""

        # Confirm that data loaded is the same as the data before it was saved.
        self.assertEqual(SYMBOL_NAME, self.repo.load(DEFAULT_STORAGE_TEST_FILENAME))

        # Confirm blank list is return from a bad filename.
        self.assertEqual(self.repo.load('bad_filename.csv'), [])

    def test_save(self):
        """Test save."""

        # Test save using the setUpClass method compared with original test data.
        self.assertEqual(self.repo.symbols_names, SYMBOL_NAME)

    def test_file_type_handler(self):
        """Test _file_type_handler."""

        # Test exception for second positional argument.
        self.assertRaises(
            StorageError,
            self.repo._file_type_handler,
            DEFAULT_STORAGE_TEST_FILENAME,
            'bad_argument'
        )

        # Test for exception when file extension is not included.
        file = DEFAULT_STORAGE_TEST_FILENAME.split('.')[0]
        self.assertRaises(
            StorageError,
            self.repo._file_type_handler,
            file,
            'load'
        )

        # Test for exception when file type is not legal.
        file = DEFAULT_STORAGE_TEST_FILENAME.split('.')[0] + '.bad'
        self.assertRaises(
            StorageError,
            self.repo._file_type_handler,
            file,
            'load'
        )

        # Test return when loading.
        self.assertEqual(
            SYMBOL_NAME,
            self.repo._file_type_handler(
                DEFAULT_STORAGE_TEST_FILENAME,
                'load'
            )
        )

        # Test return when saving.
        self.assertEqual(
            SYMBOL_NAME,
            self.repo._file_type_handler(
                DEFAULT_STORAGE_TEST_FILENAME,
                'save',
                SYMBOL_NAME
            )
        )

    def test_load_csv(self):
        """Test _load_csv."""

        # Confirm that method loads data when argument is valid.
        self.assertEqual(
            SYMBOL_NAME,
            self.repo._load_csv(DEFAULT_STORAGE_TEST_FILENAME)
        )

        # Confirm that exception with non-existent file is raised.
        self.assertRaises(
            StorageError,
            self.repo._load_csv,
            'bad_filename.csv'
        )

    def test_save_csv_and_load_csv(self):
        """Test _save_csv and _load_csv methods."""

        # Save test data to DEFAULT_STORAGE_TEST_FILENAME.
        self.repo._save_csv(SYMBOL_NAME, DEFAULT_STORAGE_TEST_FILENAME)

        # Load information from DEFAULT_STORAGE_TEST_FILENAME.
        loaded_data = self.repo._load_csv(DEFAULT_STORAGE_TEST_FILENAME)

        # Confirm that test data is the same through a saving and loading cycle.
        self.assertEqual(loaded_data, SYMBOL_NAME)


if __name__ == '__main__':
    unittest.main()
