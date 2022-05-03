#!/usr/bin/python
# -*- coding: utf-8 -*-

"""This module is used to test pull_from_yf.py"""

import copy
import unittest
from datetime import date
from dateutil.relativedelta import relativedelta

# Local imports.
from pull_from_yf import \
    _check_dates, \
    _check_symbol, \
    _get_fund_data, \
    _parse_fund_data, \
    get_yf_fund_data, \
    PullDataError
from tests.test_assets import DESIRED_DATA, RAW_FUND_DATA


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
        """Test get_fund_data."""

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

    def test_check_dates(self):
        """Test_check_dates."""

        # Valid arguments.
        self.assertTrue(_check_dates('2000-01-01', '2020-01-01'))

        with self.assertRaises(PullDataError):
            # Argument is in wrong format.
            _check_dates('20000101', '20200101')
            # Start date is the same or greater than end date.
            _check_dates('2020-01-01', '2020-01-01')
            _check_dates('2020-01-02', '2020-01-01')
            # End date is greater than the current date. end_date = tomorrow.
            _check_dates('2020-01-01', (date.today() + relativedelta(days=1)).__str__())

    def test_check_symbol(self):
        """Test _check_symbol."""

        # Test legal arguments.
        self.assertTrue(_check_symbol('aaa'))
        self.assertTrue(_check_symbol('a.aa'))
        self.assertTrue('a-aa')
        self.assertTrue('aaa.2')

        # Confirm errors are raised when structure of argument data is not legal.
        with self.assertRaises(PullDataError):
            # Argument is type int.
            _check_symbol(111)
            # Argument is too short, less than 1 character.
            _check_symbol('')
            # Argument is too long, greater than 6 characters.
            _check_symbol('12345678')
            # Fund digit value is too great.
            _check_symbol('a8a')
            # Fund uses an illegal character.
            _check_symbol('a*a')

    def test_get_yf_fund_data(self):
        """Test get_yf_fund_data."""

        pass

    def test_parse_fund_data(self):
        """Test parse_fund_data."""

        # Confirm that argument returns desired data.
        test_result = _parse_fund_data(RAW_FUND_DATA)
        self.assertEqual(DESIRED_DATA, test_result)

    def test_check_data_structure(self):
        """Test _check_data_structure."""

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

        # Test above for raised errors.
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
