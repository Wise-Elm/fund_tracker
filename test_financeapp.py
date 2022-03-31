#!/usr/bin/python
# -*- coding: utf-8 -*-

"""This module is used to test financeapp.py"""

import unittest

from core import Fund
from financeapp import FundTracker, FundTrackerApplicationError
from test_assets import ASSETS


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
        self.app.symbols_names = ASSETS  # Load test assets as saved data.
        funds = self.app.instantiate_saved_funds()  # Instantiate test assets.
        self.app.funds = funds  # Add instantiated Funds to self.app.funds.

    def tearDown(self):
        pass

    def test_functions(self):
        pass


if __name__ == '__main__':
    unittest.main()
