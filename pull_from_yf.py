#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Author:
    Graham Steeds

Context:
    Used to interface between parent application and the third party YahooFinancials
    module.

Description:
    When a request for data is received this module then requests associated data from
    YahooFinancials, checks the validity of data, then parses the data into a format
    readable by the parent application.

    The only function that should be called is def get_yf_fund_data(), which will
    coordinate with other functions to return desired data in the form of:
        list[symbol, denomination, type, list[[date, price]], name]

Attributes:
    DATE_FORMAT: Format for working with dates. (yyyy-mm-dd).
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
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from logging import handlers

# Third party imports.
from yahoofinancials import YahooFinancials


DATE_FORMAT = '%Y-%m-%d'
DEFAULT_LOG_FILENAME = 'pull_data.log'
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


class PullDataError(RuntimeError):
    """Base class for exceptions arising from this module."""


def _get_fund_data(fund, start_date, end_date):
    """Retrieve data for fund.

    Args:
        fund (str): First parameter. Fund symbol. ex. 'FBGRX'.
        start_date (str): Second parameter. Start date (yyyy-mm-dd) for data retrieval.
        end_date (str): Third parameter. End date (yyyy-mm-dd) for data retrieval.

    Returns:
        fund_data (dict) or None. Dictionary of fund data or None.
    """

    log.debug(
        f'Getting data for fund: {fund}, between {start_date} and {end_date}...')

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

    result = _get_fund_data(symbol, start_date, end_date)

    # Put data into acceptable format for caller.
    desired_data = _parse_fund_data(result)

    # Append custom saved name for fund.
    if name:
        desired_data.append(name)

    log.debug(f'get_yf_fund_data (symbol: {symbol}, name: {name}) complete.')

    return desired_data


def _parse_fund_data(data):
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
            raise PullDataError(msg)

        elif not 'dividends':
            msg = f'Data dictionary missing: dividends.'
            log.warning(msg)
            raise PullDataError(msg)

        elif 'firstTradeDate' not in v:
            msg = f'Data dictionary missing: firstTradeDate.'
            log.warning(msg)
            raise PullDataError(msg)

        elif 'currency' not in v:
            msg = f'Data dictionary missing: currency.'
            log.warning(msg)
            raise PullDataError(msg)

        elif 'instrumentType' not in v:
            msg = f'Data dictionary missing: instrumentType.'
            log.warning(msg)
            raise PullDataError(msg)

        elif 'timeZone' not in v:
            msg = f'Data dictionary missing: timeZone.'
            log.warning(msg)
            raise PullDataError(msg)

        elif 'prices' not in v:
            msg = f'Data dictionary missing: prices.'
            log.warning(msg)
            raise PullDataError(msg)

        else:
            return True


def test():
    """For development level module testing."""

    pass


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
