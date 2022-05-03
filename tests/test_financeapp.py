#!/usr/bin/python
# -*- coding: utf-8 -*-

"""This module is used to test financeapp.py"""
import random
import unittest

# Local imports.
from core import Fund
from financeapp import FundTracker, FundTrackerApplicationError
from tests.test_assets import \
    PRE_INSTANTIATED_FUND_1, \
    PRE_INSTANTIATED_FUND_2, \
    PRE_INSTANTIATED_FUND_3, \
    SYMBOL_NAME, \
    SYMBOL_NAME_2


class TestApplication(unittest.TestCase):
    """Test application.py."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Instantiate fund in __init__ to prevent repetitive instantiation for
        # each test as would be done with the setUp method.

        # Using pre-made test data stored in tests.test_assets in order to prevent
        # network calls used by dependant modules, which would complicate this test.

        # Get data for testing from test.test_assets.
        lst = [
            PRE_INSTANTIATED_FUND_1,
            PRE_INSTANTIATED_FUND_2,
            PRE_INSTANTIATED_FUND_3
        ]
        # Instantiate FundTracker without loading data.
        self.ft = FundTracker(load_data=False)
        # Populate ft.symbols_names.
        self.ft.symbols_names = [[fund[0], fund[-1]] for fund in lst]
        # Populate ft.funds with fund objects based on test data.
        self.ft.funds = [Fund(*fund) for fund in lst]

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_instantiate_saved_funds(self):
        """Test instantiate_saved_funds."""

        pass

    def test_instantiate_fund(self):
        """Test instantiate_fund."""

        pass

    def test_check_data_source(self):
        """Test check_data_source."""

        # List of available data sources, meaning linked modules available for pulling
        # data.
        sources = list(self.ft.AVAILABLE_DATA_SOURCES.keys())

        # Test for True with good data source.
        self.assertTrue(self.ft.check_data_source(random.choice(sources)))

        # Test for Error with bad data source.
        self.assertRaises(
            FundTrackerApplicationError,
            self.ft.check_data_source,
            'Invalid'  # Invalid data source.
        )

    def test_pull_yahoofinancial(self):
        """Test pull_yahoofinancial"""

        pass

    def test_save(self):
        """Test save."""

        pass

    def test_find_fund(self):
        """Test find_fund."""

        # Confirm found fund is the desired fund object.
        self.assertEqual(
            self.ft.funds[0].symbol,  # Fund symbol.
            self.ft.find_fund(self.ft.funds[0].symbol)  # Fund fund using symbol.
        )

        # Confirm found fund is None when a fund does not exist.
        self.assertEqual(None, self.ft.find_fund('INVALID'))

    def delete_fund(self):
        """Test delete_fund."""

        # Fund object for testing.
        fund = self.ft.funds[-1]

        # Confirm fund is in self.ft.funds.
        self.assertIn(fund, self.ft.funds)

        # Delete fund.
        self.delete_fund(fund.symbol)

        # Confirm fund is deleted from self.ft.funds.
        self.assertNotIn(fund, self.ft.funds)

        # Add fund back to self.ft.funds to not interfere with other testing.
        self.ft.funds.append(fund)

    def test_generate_all_fund_perf_str(self):
        """Test generate_all_fund_perf_str."""

        pass

    def test_custom_range_performance(self):
        """Test custom_range_performance."""

        pass

    def test_add_fund(self):
        """Test add_fund."""

        pass


if __name__ == '__main__':
    unittest.main()
