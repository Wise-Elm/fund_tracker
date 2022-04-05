#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Author:
    Graham Steeds

Context:
    Used for pulling data from the YahooFinancials module.

Attributes:
    DATE_FORMAT: Format for working with dates. (yyyy-mm-dd).
    DEFAULT_LOG_FILENAME: Default filename for logging when module called directly.
    DEFAULT_LOG_LEVEL: Default log level when this module is called directly.
    RUNTIME_ID: Generate a unique uuid object. Used in logging.

Composition Attributes:
    Line length = 88 characters.
"""

import logging
import uuid
from datetime import datetime
from logging import handlers

# External Imports
from yahoofinancials import YahooFinancials


DATE_FORMAT = '%Y-%m-%d'
DEFAULT_LOG_FILENAME = 'pull_data.log'  # Used when __name__ == '__main__'
DEFAULT_LOG_LEVEL = logging.WARNING
RUNTIME_ID = uuid.uuid4()

# Configure logging.
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class PullDataError(RuntimeError):
    """Base class for exceptions arising from this module."""


def get_fund_data(fund, start_date, end_date):
    """Retrieve data for fund.

    Args:
        fund (str): First parameter. Fund symbol. ex. 'FBGRX'.
        start_date (str): Second parameter. Start date (yyyy-mm-dd) for data retrieval.
        end_date (str): Third parameter. End date (yyyy-mm-dd) for data retrieval.

    Returns:
        fund_data (dict) or None. Dictionary of fund data or None.
    """

    log.debug(f'Getting data for fund: {fund}, between {start_date} and {end_date}...')

    # Check legality of fund and dates.
    if _check_dates(start_date, end_date) and _check_symbol(fund):

        yf = YahooFinancials(fund)
        fund_data = yf.get_historical_price_data(
            start_date=start_date,
            end_date=end_date,
            time_interval='daily'
        )

        if fund_data is None:
            msg = f'No data found for fund: {fund} between dates {start_date} and ' \
                  f'{end_date}. Possible timeout.'
            log.warning(msg)
            raise PullDataError(msg)

        return fund_data

    return None


def _check_dates(start_date, end_date):
    """Confirm dates are in the correct format and range.

    Args:
        start_date (str): First parameter. yyyy-mm-dd.
        end_date (str): Second parameter, yyyy-mm-dd.

    Returns:
        (Bool(True)): True when date conditions are met.

    Raises:
        ControllerForYfError (Error): When dates are in the incorrect format or start
            date is not before the end date.
    """

    try:
        start_date = datetime.strptime(start_date, DATE_FORMAT).date()
        end_date = datetime.strptime(end_date, DATE_FORMAT).date()
    except ValueError:
        msg = 'Date not in correct format: yyyy-mm-dd.'
        log.warning(msg)
        raise PullDataError(msg)

    if start_date == end_date or start_date > end_date:
        msg = f'Start date must be before end date. ' \
              f'Start date: {start_date}, End date: {end_date}.'
        log.warning(msg)
        raise PullDataError(msg)

    return True


def _check_symbol(symbol):
    """Confirm that fund symbol is legal.

    Args:
        symbol (str): Symbol for fund.

    Returns:
        (Bool(True)): True when date conditions are met.

    Raises:
        ControllerForYfError (Error): When symbol is not legal.
    """

    if type(symbol) is not str:
        msg = f'Symbol for fund my be type string. Current type: {type(symbol)}.'
        log.warning(msg)
        raise PullDataError(msg)

    elif not 0 < len(symbol) < 10:
        msg = f'Fund symbol must be between 1 and 9 characters. Current length: ' \
              f'{len(symbol)}.'
        log.warning(msg)
        raise PullDataError(msg)

    elif not symbol.isalpha():
        msg = f'All characters in fund symbol must be alphabetic. Symbol: {symbol}.'
        log.warning(msg)
        raise PullDataError(msg)

    else:
        return True


def pull_from_yf_self_test():
    """Run Unittests on module.

    Args:
        None

    Returns:
        None
    """

    import unittest

    import test_pull_from_yf

    # Conduct unittest.
    suite = unittest.TestLoader().loadTestsFromModule(test_pull_from_yf)
    unittest.TextTestRunner(verbosity=2).run(suite)


def test():
    """For development level module testing."""

    pass


if __name__ == '__main__':

    # Configure Rotating Log. Only runs when module is called directly.
    handler = handlers.RotatingFileHandler(
        filename=DEFAULT_LOG_FILENAME,
        maxBytes=100**3,  # 0.953674 Megabytes.
        backupCount=1
    )
    formatter = logging.Formatter(
        f'[%(asctime)s] - {RUNTIME_ID} - %(levelname)s - [%(name)s:%(lineno)s] - '
        f'%(message)s'
    )
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.setLevel(DEFAULT_LOG_LEVEL)

    self_test()