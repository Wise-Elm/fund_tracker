#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Context:
    Provide test assets for funanceapp.py self testing.

Attributes:
    ASSETS: list of fund attributes as it would be loaded by storage.py.
"""

from datetime import datetime

from core import DATE_FORMAT


ASSETS = [
    ['FBGRX', 'fund 1'],
    ['FNBGX', 'fund 2'],
    ['FNCMX', 'fund 3'],
    ['FPADX', 'fund 4'],
    ['FSMAX', 'fund 5']
]

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


# Example return for controller_for_yf.parse_fund_data().
DESIRED_DATA = [
    'VITPX',
    'USD',
    'MUTUALFUND',
    [['2022-04-01', 80.97000122070312]]
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


POST_INITIALIZED_FUND = [
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

INITIALIZED_FUND_STR = 'FXAIX - STOCK\nUSD - MUTUALFUND\nLatest price: 2020-01-01 - ' \
                       '$90.00'

INITIALIZED_FUND_REPR = PRE_INITIALIZED_FUND_1[0]
