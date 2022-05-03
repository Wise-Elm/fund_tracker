#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Author:
    Graham Steeds

Context:
    Provide test assets for funanceapp.py and dependant module self testing.

Attributes:
    DESIRED_DATA: Simplified example return for controller_for_yf.parse_fund_data().
    INITIALIZED_FUND_STR: Example return __str__() of fund made from attributes from
        PRE_INITIALIZED_FUND_1
    RAW_FUND_DATA: Example of return data from pull_from_yf.get_fund_data('VITPX').
    SYMBOL_NAME: List of fund attributes as it would be loaded by storage.py.
    SYMBOL_NAME_2 = List of fund attributes as it would be loaded by storage.py.
    PRE_INITIALIZED_FUND_1: Example attributes for a fund.
    PRE_INITIALIZED_FUND_2: Example attributes for a fund.
    INITIALIZED_FUND_REPR: Example return __repr__() of fund made from attributes from
        PRE_INITIALIZED_FUND_1
    POST_INITIALIZED_FUND_1: Example attributes for fund initialized using attributes
        from PRE_INITIALIZED_FUND_1: Example attributes for a fund.

Composition Attributes:
    Line length = 88 characters.
"""

from datetime import datetime

# External Imports
from core import DATE_FORMAT


# Example return for controller_for_yf.parse_fund_data().
DESIRED_DATA = [
    'VITPX',
    'USD',
    'MUTUALFUND',
    [['2022-04-01', 80.97000122070312]]
]


INITIALIZED_FUND_STR = 'FXAIX - STOCK\nUSD - MUTUALFUND\nLatest price: 2020-01-01 - ' \
                       '$90.00'

# Example argument for controller_for_yf.parse_fund_data().
RAW_FUND_DATA = {
    'VITPX':
        {'eventsData':
        {'dividends':
        {'2022-03-22':
             {'amount': 0.274, 'date': 1647955800, 'formatted_date': '2022-03-22'}}},
        'firstTradeDate': {'formatted_date': '2001-05-31', 'date': 991315800},
        'currency': 'USD',
        'instrumentType': 'MUTUALFUND',
        'timeZone': {'gmtOffset': -14400},
        'prices':
             [{'date': 1648819800, 'high': 80.97000122070312, 'low': 80.97000122070312,
                'open': 80.97000122070312, 'close': 80.97000122070312, 'volume': 0,
                'adjclose': 80.97000122070312, 'formatted_date': '2022-04-01'}]}}

SYMBOL_NAME = [
    ['FBGRX', 'fund 1'],
    ['FNBGX', 'fund 2'],
    ['FNCMX', 'fund 3'],
    ['FPADX', 'fund 4'],
    ['FSMAX', 'fund 5']
]

SYMBOL_NAME_2 = [
    ['F', 'Ford']
]

PRE_INITIALIZED_FUND_1 = [
    'FXAIX',
    'USD',
    'MUTUALFUND',
    [['2021-01-01', 91.1], ['2022-01-01', 92.2], ['2020-01-01', 90.0]],
    'STOCK'
    # 'test,
]

PRE_INITIALIZED_FUND_2 = [
    'FSMAX',
    'USD',
    'MUTUALFUND',
    [['2021-01-01', 91.1], ['2022-01-01', 92.2], ['2020-01-01', 90.0]],
    'STOCK'
    # 'test,
]

INITIALIZED_FUND_REPR = PRE_INITIALIZED_FUND_1[0]

POST_INITIALIZED_FUND_1 = [
    'FXAIX',
    'USD',
    'MUTUALFUND',
    [
        [datetime.strptime('2021-01-01', DATE_FORMAT).date(), 91.1],
        [datetime.strptime('2022-01-01', DATE_FORMAT).date(), 92.2],
        [datetime.strptime('2020-01-01', DATE_FORMAT).date(), 90.0]
    ],
    'STOCK',
    'test'
]

# Used to instantiate Fund objects.
PRE_INSTANTIATED_FUND_1 = [
    'FXAIX',
    'USD',
    'MUTUALFUND',
    [
        ['2021-01-01', 91.1],
        ['2022-01-01', 92.2],
        ['2020-01-01', 90.0]
    ],
    'test1'
]

# Used to instantiate Fund objects.
PRE_INSTANTIATED_FUND_2 = [
    'FNBGX',
    'USD',
    'MUTUALFUND',
    [
        ['2021-01-01', 91.1],
        ['2022-01-01', 92.2],
        ['2020-01-01', 90.0]
    ],
    'test2'
]

# Used to instantiate Fund objects.
PRE_INSTANTIATED_FUND_3 = [
    'FNCMX',
    'USD',
    'MUTUALFUND',
    [
        ['2021-01-01', 91.1],
        ['2022-01-01', 92.2],
        ['2020-01-01', 90.0]
    ],
    'test3'
]
