#!/usr/bin/python
# -*- coding: utf-8 -*-

"""This module is used to test financeapp.py"""
import random
import unittest
from random import choice

from core import Fund
from financeapp import FundTracker, FundTrackerApplicationError
from test_assets import SYMBOL_NAME, SYMBOL_NAME_2


class TestApplication(unittest.TestCase):
    """Test application.py."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Instantiate fund in __init__ to prevent repetitive instantiation for
        # each test.
        self.ft = FundTracker(load_data=False)
        self.ft.symbols_names = SYMBOL_NAME
        self.ft.funds = self.ft.instantiate_saved_funds()
        self.random_fund = self.ft.funds[-1]  # Pick fund for testing add and delete.

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

    def test_initialization(self):
        """Test FundTracker initialization."""

        # Confirm composition of self.symbols_names.
        self.ft.symbols_names = SYMBOL_NAME
        # Confirm items in self.ft.funds are Fund objects.
        [self.assertIsInstance(fund, Fund) for fund in self.ft.funds]

    def test_instantiate_saved_funds(self):
        """Test instantiate_saved_funds."""

        # Confirm items in self.ft.funds are Fund objects.
        [self.assertIsInstance(fund, Fund) for fund in self.ft.funds]

    def test_instantiate_fund(self):
        """Test instantiate_fund."""

        # Instantiate Fund object for testing.
        fund = self.ft.instantiate_fund(
            SYMBOL_NAME_2[0][0],
            SYMBOL_NAME_2[0][1],
        )

        # Confirm that return is a Fund object.
        self.assertIsInstance(fund, Fund)

        # Confirm Fund object attributes instantiated correctly.
        self.assertTrue(fund.symbol, SYMBOL_NAME_2[0][0])
        self.assertTrue(fund.name, SYMBOL_NAME_2[0][1])

    def test_check_data_source(self):
        """Test check_data_source."""

        sources = list(self.ft.AVAILABLE_DATA_SOURCES.keys())

        # Test for True with good data source.
        self.assertTrue(self.ft.check_data_source(random.choice(sources)))

        # Test for Error with bad data source.
        self.assertRaises(
            FundTrackerApplicationError,
            self.ft.check_data_source,
            'aaa'  # Invalid data source.
        )

    def test_pull_yahoofinancial(self):
        """Test pull_yahoofinancial.

        Method tested in the background through other tests in this module as it
        is the default for pulling testing data.
        """

        pass

    def test_save(self):
        """Test save.

        Method tested when testing storage.repo."""

        pass

    def test_find_fund(self):
        """Test find_fund."""

        # Confirm found fund is the desired fund object.
        self.assertEqual(
            self.ft.funds[0].symbol,  # Fund symbol.
            self.ft.find_fund(self.ft.funds[0].symbol)  # Fund fund using symbol.
        )

        # Confirm found fund is None when a fund does not exist.
        self.assertEqual(None, self.ft.find_fund('   '))

    def delete_fund(self):
        """Test delete_fund."""

        # Fund object for testing.
        fund = self.random_fund

        # Confirm fund is in self.ft.funds.
        self.assertIn(fund, self.ft.funds)

        # Confirm return is None when fund not found.
        self.assertEqual(None, 'aaaaa')

        # Confirm fund is deleted from self.ft.funds.
        self.assertNotIn(self.ft.funds, self.ft.delete_fund(fund.symbol))

        # Add fund back to self.ft.funds to not interfere with other testing.
        self.ft.funds.insert(0, fund)

    def test_generate_all_fund_perf_str(self):
        """Test generate_all_fund_perf_str."""
        pass


if __name__ == '__main__':
    unittest.main()
