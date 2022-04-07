#!/usr/bin/python
# -*- coding: utf-8 -*-

"""This module is used to tes core.py"""

import unittest

# External Imports
from core import CoreError, Fund
from test_assets import (
    INITIALIZED_FUND_STR,
    INITIALIZED_FUND_REPR,
    POST_INITIALIZED_FUND_1,
    PRE_INITIALIZED_FUND_1,
    PRE_INITIALIZED_FUND_2
)


class TestApplication(unittest.TestCase):
    """Test core.py."""

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        # Instantiate funds with initialized test attributes.
        self.fund_1 = Fund(*PRE_INITIALIZED_FUND_1)
        self.fund_2 = Fund(*PRE_INITIALIZED_FUND_2)

    def tearDown(self):
        pass

    def test_initialization(self):
        """Test object instantiation and initialization."""

        # Test initialized attributes against expect attributes.
        self.assertEqual(self.fund_1.symbol, POST_INITIALIZED_FUND_1[0])
        self.assertEqual(self.fund_1.currency, POST_INITIALIZED_FUND_1[1])
        self.assertEqual(self.fund_1.instrument_type, POST_INITIALIZED_FUND_1[2])
        self.assertEqual(self.fund_1.dates_prices, POST_INITIALIZED_FUND_1[3])
        self.assertEqual(self.fund_1.name, POST_INITIALIZED_FUND_1[4])

    def test__str__(self):
        """Test __str__."""

        # Test self.fund.__str__() against expected string output.
        self.assertEqual(self.fund_1.__str__(), INITIALIZED_FUND_STR)

    def test__repr__(self):
        """Test __repr__."""

        # Test self.fund.__repr__() against expected repr output.
        self.assertEqual(self.fund_1.__repr__(), INITIALIZED_FUND_REPR)

    def test__eq__(self):
        """Test __eq__."""

        # Confirm that fund finds itself to be equal.
        self.assertTrue(self.fund_1.__eq__(self.fund_1))
        # Confirm that fund finds another fund to be unequal.
        self.assertFalse(self.fund_1.__eq__(self.fund_2))

        # Confirm that fund finds the same symbol to be equal.
        self.assertTrue(self.fund_1.__eq__(PRE_INITIALIZED_FUND_1[0]))
        # Confirm that fund finds itself and a different symbol to be unequal.
        self.assertFalse(self.fund_1.__eq__(PRE_INITIALIZED_FUND_2[0]))

        # Confirm that exception is raised when argument is not a Fund or str.
        self.assertRaises(CoreError, self.fund_1.__eq__, 123)


if __name__ == '__main__':
    unittest.main()
