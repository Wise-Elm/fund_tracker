#!/usr/bin/python
# -*- coding: utf-8 -*-

"""This module is used to test controller_for_yf.py"""

import copy
import unittest

# Local imports.
from controller_for_yf import ControllerForYfError, parse_fund_data
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
        """Test get_yf_fund_data().

        Testing handled in pull_from_yf.get_fund_data() self test.
        """
        pass

    def test_parse_fund_data(self):
        """Test parse_fund_data()."""

        # Confirm that argument returns desired data.
        test_result = parse_fund_data(RAW_FUND_DATA)
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

        with self.assertRaises(ControllerForYfError):
            parse_fund_data(a)
            parse_fund_data(b)
            parse_fund_data(c)
            parse_fund_data(d)
            parse_fund_data(e)
            parse_fund_data(f)
            parse_fund_data(g)


if __name__ == '__main__':
    unittest.main()
