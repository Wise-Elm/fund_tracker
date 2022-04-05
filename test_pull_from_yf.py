#!/usr/bin/python
# -*- coding: utf-8 -*-

"""This module is used to test pull_from_yf.py"""

import copy
import unittest

# Local imports.
from pull_from_yf import get_fund_data, PullDataError


class TestApplication(unittest.TestCase):
    """Test core.py."""

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

    def test_get_fund_data(self):
        """Test get_fund_data()."""

        # Test dates.
        with self.assertRaises(PullDataError):
            # Test raise error when start date is the same or after end date.
            get_fund_data(fund='F', start_date='2000-01-01', end_date='1999-01-01')
            # Dates in wrong format.
            get_fund_data(fund='F', start_date='20000101', end_date='19990101')

        # Test symbol.
        with self.assertRaises(PullDataError):
            # Test alphabetical.
            get_fund_data(fund='123', start_date='2000-01-01', end_date='2001-01-01')
            # Test length.
            get_fund_data(fund='', start_date='2000-01-01', end_date='2001-01-01')
            get_fund_data(
                fund='1234567890',
                start_date='2000-01-01',
                end_date='2001-01-01'
            )
            # Test type.
            get_fund_data(fund=123, start_date='2000-01-01', end_date='2001-01-01')


if __name__ == '__main__':
    unittest.main()