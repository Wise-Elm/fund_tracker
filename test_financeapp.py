#!/usr/bin/python
# -*- coding: utf-8 -*-

"""This module is used to test financeapp.py"""

import unittest

from core import Fund
from financeapp import FundTracker, FundTrackerApplicationError
from test_assets import assets


class TestApplication(unittest.TestCase):
    """Test application.py."""

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.app = FundTracker(load_data=False)  # Instantiate app without saved data.
        self.app.symbols_names = assets  # Load test assets as saved data.
        funds = self.app.instantiate_saved_funds()  # Instantiate test assets.
        self.app.funds = funds  # Add instantiated Funds to self.app.funds.

    def tearDown(self):
        pass

    def test_functions(self):
        pass

    # def test_instantiate_saved_funds(self):
    #     """Test instantiate_saved_funds().
    #
    #     Assert that saved data is instantiated correctly as Fund objects.
    #     """

        # Confirm self.app.funds are Fund objects. Confirms use in setUp().
        # [self.assertIsInstance(fund, Fund) for fund in self.app.funds]

        # Confirm the correct number of funds have been instantiated.
        # Confirms use in setUp().
        # self.assertEqual(len(assets), len(self.app.funds))

        # Test exception is raised when data_source is invalid.
        # with self.assertRaises(FundTrackerApplicationError):
        #     self.app.instantiate_saved_funds(data_source='bad data source')

    # def test_instantiate_fund(self):
    #     """Test instantiate_fund()."""

        # Confirm legal data is instantiated info Fund objects.
        # self.assertIsInstance(
        #     self.app.instantiate_fund(assets[0][0], name=assets[0][1]),
        #     Fund
        # )

        # Confirm bad data raises an exception.
        # with self.assertRaises(FundTrackerApplicationError):
        #     self.app.instantiate_fund(symbol='bad symbol')

        # Test exception is raised when data_source is invalid.
        # with self.assertRaises(FundTrackerApplicationError):
        #     self.app.instantiate_saved_funds(data_source='bad data source')


if __name__ == '__main__':
    unittest.main()
