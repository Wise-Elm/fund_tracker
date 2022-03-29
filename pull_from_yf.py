#!/usr/bin/python
# -*- coding: utf-8 -*-


import logging
import uuid
from logging import handlers

from yahoofinancials import YahooFinancials


DEFAULT_CORE_LOG_FILENAME = 'pull_data'  # Used when __name__ == '__main__'
CORE_LOG_LEVEL = logging.DEBUG
RUNTIME_ID = uuid.uuid4()

# Configure logging.
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class PullDataError(RuntimeError, KeyError, ValueError, BaseException):
    """Base class for exceptions arising from this module."""


def get_fund_data(fund, start_date, end_date):
    """Retrieve data for fund.

    Args:
        fund (str): First parameter. Fund symbol. ex. 'FBGRX'.
        start_date (str): Second parameter. Start date (yyyy-mm-dd) for data retrieval.
        end_date (str): Third parameter. End date (yyyy-mm-dd) for data retrieval.

    Returns:
        yearly_close (dict) or None. Dictionary of fund data or None.
    """

    log.debug(f'Getting data for fund: {fund}, between {start_date} and {end_date}...')

    yearly_close = None

    try:
        yf = YahooFinancials(fund)
        yearly_close = yf.get_historical_price_data(
            start_date=start_date,
            end_date=end_date,
            time_interval='daily'
        )

    except PullDataError:
        msg = f'Error pulling data from source for {fund}.'
        log.warning(msg)

    finally:

        if yearly_close is None:
            log.debug(f'No data found for fund: {fund} between dates {start_date} and '
                      f'{end_date}.')
        else:
            log.debug(f'Data found for fund: {fund}.')
            return yearly_close


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
        filename=DEFAULT_CORE_LOG_FILENAME,
        maxBytes=100**3,
        backupCount=1
    )
    formatter = logging.Formatter(
        f'[%(asctime)s] - {RUNTIME_ID} - %(levelname)s - [%(name)s:%(lineno)s] - '
        f'%(message)s'
    )
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.setLevel(CORE_LOG_LEVEL)

    self_test()