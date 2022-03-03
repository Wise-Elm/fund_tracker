#!/usr/bin/python
# -*- coding: utf-8 -*-

__version__ = '0.1.0'

"""Application.

Context:

Description:

Attributes:
    DEFAULT_LOG_FILENAME (str): Default file path for application wide logging.
    DEFAULT_LOG_LEVEL (:obj: 'int'): Integer represents a value which assigns a log 
        level from logging.
    RUNTIME_ID (:obj: uuid): Generate a unique uuid object.

Composition Attributes:
    Line length = 88 characters.
"""


import argparse
import logging
import sys
import uuid
from logging import handlers

from core import CoreError, Fund
from pull_data import get_fund_data
from storage import StorageError


DEFAULT_LOG_FILENAME = 'financeapp.log'
DEFAULT_LOG_LEVEL = logging.DEBUG
RUNTIME_ID = uuid.uuid4()


# Configure logging.
log = logging.getLogger()
log.addHandler(logging.NullHandler())


class FundTrackerApplicationError(RuntimeError):
    """Base class for exceptions arising from this module."""


class FundTracker:

    def __init__(self):
        # self.repo = Repo()

        self.symbols = ['FBGRX', 'FNCMX', 'FPADX']
        #   Example:
        #       self.funds = ['F', 'FBGRX', 'TSLA']

        self.funds = []


    def instantiate_funds(self):
        symbols = self.symbols or None
        if symbols:
            for symbol in symbols:
                data = get_fund_data(symbol)
                if not data:
                    continue
                fund_data = self.parse_fund_data(data)
                if not fund_data:
                    continue
                fund = Fund(*fund_data)
                self.funds.append(fund)
        return

    def parse_fund_data(self, data):
        key = tuple(data.keys())
        symbol = key[0]
        currency = data[symbol]['currency']
        instrument_type = data[symbol]['instrumentType']
        all_dates_prices = data[symbol]['prices']
        dates_prices = \
            [(day['formatted_date'], day['close']) for day in all_dates_prices]

        desired_data = symbol, currency, instrument_type, dates_prices
        return None or desired_data

    def _print(self):
        for fund in self.funds:
            print(fund)


    def main_event_loop(self):
        """Run application.

        Provides a user-friendly interaction with program from shell. Program
        stays running until user quits.

        Args:
            None

        Returns:
            None
        """

        log.debug('Entering Main Event Loop...')

        pass

        log.debug('Main Event Loop has ended.')

        return


def parse_args(argv=sys.argv):
    """Setup shell environment to run program."""

    log.debug('parse_args...')

    # Program description.
    parser = argparse.ArgumentParser(
        description='Description for program.',
        epilog='epilog here.'
    )

    # What this argument will do.
    parser.add_argument(
        '-t',
        '--test',
        help='Run testing on application and exit',
        action='store_true',
        default=False
    )

    args = parser.parse_args()  # Collect arguments.

    log.debug(f'args: {args}')
    log.debug('parse_args complete.')

    return args


def run_application(args):
    """Run application based on shell commands.

    Args:
        args (List [args]): List of arguments from argument parser.

    Returns:
        None
    """

    # Skip instantiating Application if self testing is selected.
    if args.test:
        log.debug('Begin unittests...')

        self_test()  # Test application.py

        log.debug('Unittests complete.')

        return

    app = FundTracker()  # Begin application instance.
    log.debug('Application instantiated.')

    # if args.something:
    #     do something
    #     return

    # Run Application main event loop when no args are True.
    app.main_event_loop()
    return


def self_test():
    """Run Unittests on module.

    Args:
        None

    Returns:
        None
    """

    import unittest

    import test_financeapp

    # Conduct unittest.
    suite = unittest.TestLoader().loadTestsFromModule(test_financeapp)
    unittest.TextTestRunner(verbosity=2).run(suite)


def test():
    """For development level module testing."""

    ft = FundTracker()
    ft.instantiate_funds()
    ft._print()


def main():
    # Configure Rotating Log.
    handler = handlers.RotatingFileHandler(
        filename=DEFAULT_LOG_FILENAME,
        maxBytes=100 ** 3,  # 0.953674 Megabytes.
        backupCount=1)
    formatter = logging.Formatter(
        f'[%(asctime)s] - {RUNTIME_ID} - %(levelname)s - [%(name)s:%(lineno)s] - '
        f'%(message)s'
    )
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.setLevel(DEFAULT_LOG_LEVEL)

    log.debug('main...')

    args = parse_args()
    run_application(args)

    log.debug('main complete.')


if __name__ == '__main__':
    # main()
    test()


