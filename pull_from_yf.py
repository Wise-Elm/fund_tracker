#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Author:
    Graham Steeds

Context:
    Used for pulling data from the YahooFinancials module.

Attributes:
    DEFAULT_LOG_FILENAME: Default filename for logging when module called directly.
    DEFAULT_LOG_LEVEL: Default log level when this module is called directly.
    RUNTIME_ID: Generate a unique uuid object. Used in logging.

Composition Attributes:
    Line length = 88 characters.
"""

import logging
import uuid
from logging import handlers

from yahoofinancials import YahooFinancials


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

    fund_data = None

    try:
        yf = YahooFinancials(fund)
        fund_data = yf.get_historical_price_data(
            start_date=start_date,
            end_date=end_date,
            time_interval='daily'
        )

    except BaseException as be:
        msg = f'Error pulling data from source for {fund}.'
        log.warning(msg)
        raise PullDataError(msg)

    finally:

        if fund_data is None or not fund_data[fund]['prices']:
            log.warning(f'No data found for fund: {fund} between dates {start_date} '
                        f'and {end_date}. Possible thread timeout.')
        else:
            if fund == 'ASDF':
                print(fund_data)
            log.debug(f'Data found for fund: {fund}.')

        return fund_data


def self_test():
    """Run Unittests on module.

    Args:
        None

    Returns:
        None
    """

    import unittest

    import test_pull_data

    # Conduct unittest.
    suite = unittest.TestLoader().loadTestsFromModule(test_pull_data)
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