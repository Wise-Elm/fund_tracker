#!/usr/bin/python
# -*- coding: utf-8 -*-

"""This module is used to test pull_from_yf.py"""

import copy
import unittest

# Local imports.
from pull_from_yf import _get_fund_data, _parse_fund_data, PullDataError
from test_assets import DESIRED_DATA, RAW_FUND_DATA


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

    def test_get_yf_fund_data(self):
        """Test get_fund_data()."""

        # Test dates.
        with self.assertRaises(PullDataError):
            # Test raise error when start date is the same or after end date.
            _get_fund_data(fund='F', start_date='2000-01-01', end_date='1999-01-01')
            # Dates in wrong format.
            _get_fund_data(fund='F', start_date='20000101', end_date='19990101')

        # Test symbol.
        with self.assertRaises(PullDataError):
            # Test alphabetical.
            _get_fund_data(fund='123', start_date='2000-01-01', end_date='2001-01-01')
            # Test length.
            _get_fund_data(fund='', start_date='2000-01-01', end_date='2001-01-01')
            _get_fund_data(
                fund='1234567890',
                start_date='2000-01-01',
                end_date='2001-01-01'
            )
            # Test type.
            _get_fund_data(fund=123, start_date='2000-01-01', end_date='2001-01-01')

    def test_parse_fund_data(self):
        """Test parse_fund_data()."""

        # Confirm that argument returns desired data.
        test_result = _parse_fund_data(RAW_FUND_DATA)
        self.assertEqual(DESIRED_DATA, test_result)

        # Confirm errors are raised when structure of argument data is not legal.
        a = copy.deepcopy(RAW_FUND_DATA)
        a['VITPX'] = a['VITPX'].pop('eventsData')

        b = copy.deepcopy(RAW_FUND_DATA)
        b['VITPX']['eventsData'].pop('dividends')

        c = copy.deepcopy(RAW_FUND_DATA)
        c['VITPX'].pop('firstTradeDate')

        d = copy.deepcopy(RAW_FUND_DATA)
        d['VITPX'].pop('currency')

        e = copy.deepcopy(RAW_FUND_DATA)
        e['VITPX'].pop('instrumentType')

        f = copy.deepcopy(RAW_FUND_DATA)
        f['VITPX'].pop('timeZone')

        g = copy.deepcopy(RAW_FUND_DATA)
        g['VITPX'].pop('prices')

        with self.assertRaises(PullDataError):
            _parse_fund_data(a)
            _parse_fund_data(b)
            _parse_fund_data(c)
            _parse_fund_data(d)
            _parse_fund_data(e)
            _parse_fund_data(f)
            _parse_fund_data(g)


if __name__ == '__main__':
    unittest.main()
