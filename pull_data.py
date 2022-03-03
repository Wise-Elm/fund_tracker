#!/usr/bin/python
# -*- coding: utf-8 -*-


import logging
import uuid
from datetime import date
from logging import handlers
from dateutil.relativedelta import relativedelta

from yahoofinancials import YahooFinancials


DEFAULT_CORE_LOG_FILENAME = 'pull_data'  # Used when __name__ == '__main__'
CORE_LOG_LEVEL = logging.WARNING
RUNTIME_ID = uuid.uuid4()

CURRENT_DATE = date.today().__str__()
YEAR_AGO_DATE = (date.today() - relativedelta(years=1)).__str__()
MONTH_AGO_DATE = (date.today() - relativedelta(months=1)).__str__()
WEEK_AGO_DATE = (date.today() - relativedelta(weeks=1)).__str__()

# Configure logging.
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class PullDataError(RuntimeError, KeyError, ValueError, BaseException):
    """Base class for exceptions arising from this module."""


def get_fund_data(fund):
    try:
        yf = YahooFinancials(fund)
        yearly_close = yf.get_historical_price_data(
            start_date=YEAR_AGO_DATE,
            end_date=CURRENT_DATE,
            time_interval='daily'
        )
    except PullDataError as pde:
        msg = f'Error pulling data from source for {fund}.'
        log.warning(msg)
    finally:
        return None or yearly_close


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