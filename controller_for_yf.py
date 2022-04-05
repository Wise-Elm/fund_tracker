#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Author:
    Graham Steeds

Context:
    Used to interface between parent application and pull_from_yf.py.

Description:
    Uses the pull_from_yf.py module to pull data from YahooFinancials.

Attributes:
    DEFAULT_LOG_FILENAME: Default filename for logging when module called directly.
    DEFAULT_LOG_LEVEL: Default log level when this module is called directly.
    RUNTIME_ID: Generate a unique uuid object. Used in logging.
    CURRENT_DATE: String representing the current date in yyyy-mm-dd format.
    WEEK_AGO_DATE: String representing the date a week before the current date in
        yyyy-mm-dd format. Used when generating default dates data.
    MONTH_AGO_DATE: String representing the date a month before the current date in
        yyyy-mm-dd format. Used when generating default dates data.
    TWO_YEARS_AGO_DATE: String representing the date two years before the current date
        in yyyy-mm-dd format. Used when generating default dates data.

Composition Attributes:
    Line length = 88 characters.
    """

import logging
import uuid
from datetime import date
from dateutil.relativedelta import relativedelta
from logging import handlers

# Local imports.
from pull_from_yf import get_fund_data


DEFAULT_LOG_FILENAME = 'controller_for_yf.log'
DEFAULT_LOG_LEVEL = logging.WARNING
RUNTIME_ID = uuid.uuid4()

# Date related attributes.
CURRENT_DATE = date.today().__str__()
WEEK_AGO_DATE = (date.today() - relativedelta(weeks=1)).__str__()
MONTH_AGO_DATE = (date.today() - relativedelta(months=1)).__str__()
TWO_YEARS_AGO_DATE = (date.today() - relativedelta(years=2)).__str__()


# Configure logging.
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class ControllerForYfError(RuntimeError):
    """Base class for exceptions arising from this module."""


def get_yf_fund_data(
        symbol,
        name=None,
        start_date=TWO_YEARS_AGO_DATE,
        end_date=CURRENT_DATE
):
    """Get fund data from yahoofinancial between date arguments.

    Data will include 1 week prior to start date to give flexibility when dates land
    on holidays that do not return market information.

    Args:
        symbol (str): First parameter. Symbol for Fund. Ex: 'FXAIX'.
        name (str): Second parameter. OPTIONAL. An unofficial unique
                identifying name chosen by user to represent fund.
        start_date (str): Third parameter. OPTIONAL. Start date for date range.
        end_date (str): Fourth parameter. OPTIONAL. End date for date range.

    Returns:
        desired_data (list[symbol, denomination, type, list[[date, price]], name]):
            List of fund data or None.
    """

    log.debug(f'get_yf_fund_data (symbol: {symbol}, name: {name})...')

    result = get_fund_data(symbol, start_date, end_date)

    # Put data into acceptable format for caller.
    desired_data = parse_fund_data(result)

    # Append custom saved name for fund.
    if name:
        desired_data.append(name)

    log.debug(f'get_yf_fund_data (symbol: {symbol}, name: {name}) complete.')

    return desired_data


def parse_fund_data(data):
    """Convert pulled data from YahooFinancials into a list of desired
    fund attributes.

    Args:
        data (dict): Dictionary containing raw fund data from
            YahooFinancials.
            Example:
                {
                'symbol':{
                    ...
                    'currency':{'USD'},
                    'instrumentType':{'MUTUALFUND'},
                    'prices':[['date', price: int]]}
                    }
                }

    Returns:
        None or desired_data (list): List containing desired data from
            argument data dictionary.
            Example:
                ['symbol', 'currency', 'instrument type', [[dates & prices]]]
    """

    # Show symbol for fund being parsed.
    log.debug('Parse fund data ({})...'.format([k for k in data][0]))

    # Check the structure of the argument.
    if not _check_data_structure(data):
        return None

    key = tuple(data.keys())
    symbol = key[0]
    currency = data[symbol]['currency']
    instrument_type = data[symbol]['instrumentType']
    all_dates_prices = data[symbol]['prices']
    dates_prices = \
        [[day['formatted_date'], day['close']] for day in all_dates_prices]

    desired_data = [symbol, currency, instrument_type, dates_prices]

    # Show symbol for fund being parsed.
    log.debug('Parse fund data ({}) complete.'.format([k for k in data][0]))

    return None or desired_data


def _check_data_structure(data):
    """Confirm the structure of data.

    Args:
        data (dict[other dict & lists]): Data with complex structure.

    Returns:
        (Bool(True)): True when date conditions are met.

    Raises:
        ControllerForYfError (Error): When data structure is not legal.
    """

    for k, v in data.items():
        if not 'eventsData':
            msg = f'Data dictionary missing: eventsData.'
            log.warning(msg)
            raise ControllerForYfError(msg)

        elif not 'dividends':
            msg = f'Data dictionary missing: dividends.'
            log.warning(msg)
            raise ControllerForYfError(msg)

        elif 'firstTradeDate' not in v:
            msg = f'Data dictionary missing: firstTradeDate.'
            log.warning(msg)
            raise ControllerForYfError(msg)

        elif 'currency' not in v:
            msg = f'Data dictionary missing: currency.'
            log.warning(msg)
            raise ControllerForYfError(msg)

        elif 'instrumentType' not in v:
            msg = f'Data dictionary missing: instrumentType.'
            log.warning(msg)
            raise ControllerForYfError(msg)

        elif 'timeZone' not in v:
            msg = f'Data dictionary missing: timeZone.'
            log.warning(msg)
            raise ControllerForYfError(msg)

        elif 'prices' not in v:
            msg = f'Data dictionary missing: prices.'
            log.warning(msg)
            raise ControllerForYfError(msg)

        else:
            return True


def test():
    """For development level module testing."""

    pass


def controller_for_yf_self_test():
    """Run Unittests on module.

    Args:
        None

    Returns:
        None
    """

    import unittest

    import test_controller_for_yf

    # Conduct unittest.
    suite = unittest.TestLoader().loadTestsFromModule(test_controller_for_yf)
    unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == '__main__':

    # Configure Rotating Log. Only runs when module is called directly.
    handler = handlers.RotatingFileHandler(
        filename=DEFAULT_LOG_FILENAME,
        maxBytes=100 ** 3,  # 0.953674 Megabytes.
        backupCount=1
    )
    formatter = logging.Formatter(
        f'[%(asctime)s] - {RUNTIME_ID} - %(levelname)s - [%(name)s:%(lineno)s] - '
        f'%(message)s'
    )
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.setLevel(DEFAULT_LOG_LEVEL)

    controller_for_yf_self_test()
