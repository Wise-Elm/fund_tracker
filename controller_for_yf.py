#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
Author:
    Graham Steeds

Context:
    Used to interface between parent application and pull_from_yf.py.

Description:
    Uses the pull_from_yf.py module to pull data from YahooFinancials.

    When using child module sets up a thread class with a return value, receives either
    return value or default value upon timeout. If return value is not a timeout,
    parses value and return a data set that is acceptable by caller method.

Attributes:
    DEFAULT_LOG_FILENAME: Default filename for logging when module called directly.
    DEFAULT_LOG_LEVEL: Default log level when this module is called directly.
    DEFAULT_THREAD_TIMEOUT: Number of seconds before the thread should time out.
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
import threading
import time
import uuid
from datetime import date
from dateutil.relativedelta import relativedelta
from logging import handlers

from pull_from_yf import get_fund_data

DEFAULT_LOG_FILENAME = 'controller_for_yf.log'
DEFAULT_LOG_LEVEL = logging.WARNING
DEFAULT_THREAD_TIMEOUT = 1  # In seconds.
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


class ReturnThreadValue(threading.Thread):
    """Child class of threading.Thread.

    Constructed to provide a return value to parent.join() for thread of self.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.result = None  # Add self.result for return value.

        """Should always be called with keyword arguments from parent class.
        
        Intended arguments listed. Additional arguments available through parent class.
        
        Args:
            target (callable obj): Function to be called by run() method.
            args (list[arguments]): List of arguments to be supplied to target method.
            name (str): OPTIONAL. Name for thread.
        """

    def run(self):
        """Represents the activity of the thread.

        Adapted from parent class to provide self.result with a return value.

        Args:
            None

        Returns:
            None

        Raises:
            ControllerForYfError (Exception): Raised when self._target (function to be
                called) is not found.
        """

        log.debug(f'Thread-{self.name}.run()')

        if self._target is not None:
            # Identify return value for target function.
            self.result = self._target(*self._args, **self._kwargs)
        else:
            msg = f'Target function for Thread-{self.name} not found.'
            log.warning(msg)
            raise ControllerForYfError(msg)

    def join(self, *args, **kwargs):
        """Wait until thread terminates or timeout reached.

        Adds functionality to parent class by provide a return value to thread upon
        termination.

        Args:
            timeout (float): OPTIONAL. Number of maximum seconds before a return.

        returns:
            self.result (return value): Return value self._target (callable function).
                Defaults to None if timeout reached before callable function returns a
                value.
        """

        log.debug(f'Thread-{self.name}.join()')

        super().join(*args, **kwargs)
        return self.result


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

    # Setup thread instance to call intended function with args.
    thread = ReturnThreadValue(
        target=get_fund_data,
        args=[symbol, start_date, end_date],
        name=symbol
    )

    start_time = time.perf_counter()  # Time operation.

    thread.start()  # Start thread.

    # Result from callable function, or None if DEFAULT_THREAD_TIMEOUT is reached.
    result = thread.join(DEFAULT_THREAD_TIMEOUT)

    end_time = time.perf_counter()
    total_time = round(end_time - start_time, 2)

    log.debug(f'Thread-{thread.name} finished in {total_time} seconds.')

    # Return Error is thread timed out.
    if result is None:
        msg = f'Thread for {symbol} timed out.'
        log.warning(msg)
        return None

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


def test():
    """For development level module testing."""

    pass


def self_test():
    """Run Unittests on module.

    Args:
        None

    Returns:
        None
    """

    import unittest

    import test_storage

    # Conduct unittest.
    suite = unittest.TestLoader().loadTestsFromModule(test_storage)
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

    self_test()
