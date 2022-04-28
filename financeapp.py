#! /usr/bin/python3.10
# -*- coding: utf-8 -*-

__version__ = '0.1.0'

"""Application working title: financeapp.

Author:
    Graham Steeds

Context:
    An application derived to learn python and be ideal for use as a Cron Job.
    
    This module incorporates foreign modules to retrieve data, and handles simultaneous 
    data collection through the use of Multithreading while managing dependencies, 
    abstraction leaks, and errors.

Description:
    financeapp provides the user with an easy way to track the current and past history 
    of money market accounts. The user may create a list of funds to save, incorporating 
    optional custom fund names, and view the financial history of those funds. 
    
    Users are able to add funds including choosing what to name a fund, as well as the 
    the ability to delete, edit, and view data from custom date ranges.
    
    financeapp is designed to be easily expandable, being able to quickly incorporate 
    new financial data applications in order to retrieve data.

Extendability:
    financeapp is setup to allow easy extendability in the form of specifying custom 
    file names for saving and loading data, with the ability of have multiple data sets.
    
    Adding modules for retrieving data from different sources is easily incorporated. 
    To do so one must include the module in the FundTracker class attribute 
    self.AVAILABLE_DATA_SOURCES, so that a name for the data sources is the key and a 
    FundTracker method is the value. A custom method that handles the fund must be 
    created to pull data from the new module.
    
    The data returned must be a list of data for each fund where:
    
        list[0] = symbol (ex. 'FXAIX')
        list[1] = denomination (ex. 'USD')
        list[2] = 'type' (ex. 'MUTUALFUND')
        list[3] = [date, closing price] 
            (ex. [
                ['2021-03-09', 166.02999877929688], 
                ['2021-03-10', 164.02999877929688]
                ], 
            list[3] is ordered by date, the most current date being list[:-1].)
            
    When these parameters are met financeapp can work with any outside data gathering 
    module.
    
    If desired, financeapp is prepared to run through a main event loop to have program 
    run in a persistent mode. Do this through development using 
    FundTracker.main_event_loop().
    
    Attribute DATE_FORMAT must match in each dependant module.

Attributes:
    DATE_FORMAT: Format for working with dates. (yyyy-mm-dd).
    DEFAULT_DATA_FILE: Default file name for saving and loading data.
    DEFAULT_DATA_SOURCE: Default source for retrieving data.
    DEFAULT_LOG_FILENAME: Default file path for application wide logging.
    DEFAULT_LOG_LEVEL: Default log level.
    DEFAULT_THREAD_TIMEOUT: Number of seconds before the thread should time out.
    RUNTIME_ID: Generate a unique uuid object. Used in logging.

Composition Attributes:
    Line length = 88 characters.
    
TODO:
    Incorporate more robust error and exception handling.
    Develop unittesting.
    
    Develop error handling when input fund does not exist.
"""

import argparse
import logging
import sys
import time
import uuid
import bisect

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from logging import handlers

# Local imports.
from core import core_self_test, Fund
from controller_for_yf import get_yf_fund_data, controller_for_yf_self_test
from customthread import RTV as rtv
from pull_from_yf import pull_from_yf_self_test
from storage import Repo, storage_self_test


DATE_FORMAT = '%Y-%m-%d'
DEFAULT_DATA_FILE = 'data.csv'
DEFAULT_DATA_SOURCE = 'yahoofinance'
DEFAULT_LOG_FILENAME = 'financeapp.log'
DEFAULT_LOG_LEVEL = logging.DEBUG
DEFAULT_THREAD_TIMER = 0.8  # In seconds.
RUNTIME_ID = uuid.uuid4()

# Configure logging.
log = logging.getLogger()
log.addHandler(logging.NullHandler())


class FundTrackerApplicationError(RuntimeError):
    """Base class for exceptions arising from this module."""


class FundTracker:
    """Application for tracking and displaying stock market data.

    Class level parameters:
        self.AVAILABLE_DATA_SOURCES (dict['name': class method]):
            Dictionary containing names and associated class methods for linked external
            modules for retrieving fund data. Must be update when adding external data
            retrieval modules.

    Args:
        load_data (bool): Defaults to True. True loads saved data when available.
        data_file (str): Defaults to data.csv. File name to save and load data.
        data_source (str): Defaults to yahoofinance. Module from which to load fund
            data.
    """

    def __init__(self,
                 load_data=True,
                 data_file=DEFAULT_DATA_FILE,
                 data_source=DEFAULT_DATA_SOURCE
                 ):

        self.AVAILABLE_DATA_SOURCES = {'yahoofinance': self.pull_yahoofinancial}

        self.repo = Repo(load_data=load_data, data_file=data_file)
        self.symbols_names = self.repo.symbols_names  # ex: ['F', 'FXAIX']
        self.funds = self.instantiate_saved_funds(data_source)  # [Fund objects]

    def instantiate_saved_funds(self, data_source=DEFAULT_DATA_SOURCE):
        """Generate a list of Fund objects based on saved data.

        data_source indicates which application to use when getting fund data.

        Multithreading incorporated due to much of the processing time spent waiting
        on IO bound operations, such as waiting on network sockets.

        Args:
            data_source (str): OPTIONAL. Uses a default data source when argument is
                blank.

        Returns:
            instantiated_funds ([fund obj]): List of Fund objects.
        """

        log.debug(f'Instantiate saved funds. Data source: {data_source}...')

        start_time = time.perf_counter()  # Time operation.

        # Use custom thread class (rtv) to get return values from called method.
        # Construct list of thread objects.
        threads = [rtv(target=self.instantiate_fund,
                       args=[s_n[0], s_n[1], data_source, False])
                   for s_n in self.symbols_names]

        # Execute threads.
        [thread.start() for thread in threads]

        # Collect results.
        instantiated_funds = [thread.join(DEFAULT_THREAD_TIMER) for thread in threads]

        end_time = time.perf_counter()
        total_time = round(end_time - start_time, 2)

        log.debug(f'Instantiate saved funds completed in {total_time} seconds.')

        return instantiated_funds

    def instantiate_fund(
            self,
            symbol,
            name=None,
            data_source=DEFAULT_DATA_SOURCE,
            start_date=None,
            end_date=None,
            _create_thread=True
    ):
        """Instantiate a Fund object.

        Uses self.check_data_source() to confirm legality of data_source argument.

        Args:
            symbol (str): Symbol representing a fund. ex 'FXAIX'.
            name (str or None): OPTIONAL. Defaults to None. A customizable name for
                fund.
            data_source (str): OPTIONAL. Defaults to a usable data source. A module from
                which to pull fund data.
            start_date (str): OPTIONAL. Defaults to None.
            end_date (str): OPTIONAL. Defaults to None.
            _create_thread (Bool): For internal use only. Should not be used. When True
                method will setup a thread for setting a max time on data retrieval.

        Returns:
            (fund or None): fund when data_source is legal, and fund is found
            matching the symbol parameter. None otherwise.
        """

        log.debug(f'Instantiate fund using symbol: {symbol}, name: {name}, '
                  f'data_source: {data_source}...')

        # Will raise exception if data_source is not legal.
        self.check_data_source(data_source)

        # Identify method connecting to external module for pulling data.
        source_method = self.AVAILABLE_DATA_SOURCES[data_source]

        # Threading used to set max time for operation.
        if _create_thread is True:
            log.debug(f'Creating thread for {symbol}...')

            thread = rtv(target=source_method, args=[symbol, start_date, end_date])
            thread.start()
            data = thread.join(DEFAULT_THREAD_TIMER)

            log.debug(f'Thread for {symbol} completed.')

        # When method is called by self.instantiate_saved_funds(), since that method
        # already incorporates threading.
        else:
            # Get fund data from source method. Will return None if data is not
            # available.
            data = source_method(symbol)

        if data is None:
            return None

        if name:  # Add optional name parameter string.
            data.append(name)
        fund = Fund(*data)  # Instantiate fund object.

        log.debug(f'Instantiate fund ({fund}) complete.')

        return fund

    def check_data_source(self, data_source):
        """Determine legality of data_source.

        Example:
            If data_source = 'yahoofinance', is 'yahoofiance' a key in
            self.AVAILABLE_DATA_SOURCES.

        Args:
            data_source (str): Source module for generating data.

        Returns:
            (True or FundTrackerApplicationError): True when data_source is legal,
                FundTrackerApplicationError otherwise.
        """

        log.debug(f'Check legality of data source: {data_source}...')

        if data_source in self.AVAILABLE_DATA_SOURCES:
            log.debug(f'Data source: {data_source} is legal.')
            return True
        else:
            msg = f'Data source not available. Available data sources: ' \
                  f'{self.AVAILABLE_DATA_SOURCES}.'
            log.warning(msg)
            raise FundTrackerApplicationError(msg)

    def pull_yahoofinancial(self, symbol, start_date=None, end_date=None):
        """Get fund data from yahoofinancial module.

        When start_date and end_date are included method will return data for fund
        between those ranges.

        Args:
            symbol (str): First parameter. Symbol of fund on which to pull data. Ex:
                FXAIX.
            start_date (str): Second parameter. OPTIONAL. 'yyyy-mm-dd'. Start date for
                custom date range. Will default to one year and one week prior to
                current date.
            end_date (str): Third paramter. OPTIONAL. 'yyyy-mm-dd'. End date for custom
                date range. Will default to current date.

        Returns:
            data (list[symbol, denomination, type, list[[date, price]]]):
                List of fund data.
        """

        log.debug(f'Pulling data for fund ({symbol}) from yahoofinancial...')

        # None because second argument in get_yf_fund_data() is optional name which is
        # not currently being used.
        args = [symbol, None]
        if start_date:
            args.append(start_date)
        if end_date:
            args.append(end_date)

        # Pull data from yahoofinancial.
        data = get_yf_fund_data(*args)

        log.debug(f'Pulling data for fund ({symbol}) from yahoofinancial complete.')

        return data

    def save(self, data=None, data_file=False):
        """Saves data.

        Must be .csv file type. Saves fund symbol and name if name is populated.

        Args:
            data (None or list[Fund]): First parameter. Defaults to None. Saves
                data from self.funds when None, saves supplied list data otherwise.
            data_file (str or False): Second parameter. OPTIONAL. String representing a
                file name to save data. '.csv' is the only supported file type. Will
                create new file with that name if one does not exist. If False, will use
                default file name.

        Returns: None
        """

        log.debug('Save...')

        # Check for unique data_file.
        if not data_file:
            data_file = DEFAULT_DATA_FILE

        # Check for unique data.
        if not data:
            data = self.funds
        self.repo.save(data, data_file)

    def find_fund(self, symbol):
        """Finds and returns Fund object if it exists.

        Args:
            symbol: (str): Symbol representing a fund.

        Returns:
            fund (Fund or None): Fund object if found, None otherwise.
        """

        log.debug(f'Find fund ({symbol})...')

        for existing_fund in self.funds:
            if existing_fund == symbol:
                fund = existing_fund
                return fund

        log.debug(f'Find fund ({symbol}) complete.')

        return None

    def delete_fund(self, symbol):
        """Delete indicated fund.

        Args:
            symbol (str): String representation of fund to delete.

        Returns:
            success (Fund or False): Fund if successful, False otherwise.
        """

        log.debug(f'Delete fund ({symbol})...')

        # Find fund.
        fund = self.find_fund(symbol)
        if fund is None:
            return False

        # Remove fund from self.funds.
        self.funds.remove(fund)

        log.debug(f'Delete fund  ({symbol}) complete.')

        return fund

    def generate_all_fund_perf_str(self, day=True, week=True, year=True):
        """Generates previous 24 hour, week, and year performance of all funds
        depending on arguments.

        Args:
            day (Bool): Defaults to True. When true includes previous day fund
                performance in return.
            week (Bool): Defaults to True. When true includes previous week
                fund performance in return.
            year (Bool): Defaults to True. When true includes previous year
                fund performance in return.

        Returns:
            all_performance (str): String including general fund information as
                well time based performance data depending on arguments.
        """

        log.debug('Generate all fund perf str...')

        all_performance = ''
        kvargs = day, week, year
        for fund in self.funds:
            all_performance += '\n' + fund.generate_fund_performance_str(*kvargs)
            all_performance += '\n' + '*' * 40

        log.debug('Generate all fund perf str complete.')

        return all_performance

    def custom_range_performance(self, symbol, start_date, end_date):
        """Get the performance of a fund over a specified date range.

        Args:
            symbol (str): Fund symbol:
                Example:
                    'FXAIX'
            start_date (str): Date in format yyyy-mm-dd.
            end_date (str): Date in format yyyy-mm-dd.

        Returns:
            tuple(
                difference:float,
                start_date:datetime object,
                end_date:datetime object,
                fund:Fund object
            )
        """

        log.debug(f'Custom range performance ({symbol})...')

        today = date.today()
        start_date = datetime.strptime(start_date, DATE_FORMAT).date()
        end_date = datetime.strptime(end_date, DATE_FORMAT).date()

        # Raise exception if end date is the same or before start date.
        if end_date <= start_date:
            msg = f'Start date({start_date.__str__()}) must be before end date ' \
                  f'({end_date.__str__()}).'
            log.warning(msg)
            raise FundTrackerApplicationError(msg)

        # Raise exception if end date is in the future.
        if end_date > today:
            msg = f'End date ({end_date.__str__()}) is out of range (in the future).'
            log.warning(msg)
            raise FundTrackerApplicationError(msg)

        # Include an additional week before the start date to make up for dates where
        # pricing and/or dates are not available.
        start_plus_week = start_date - relativedelta(weeks=1)

        fund = self.instantiate_fund(
            symbol,
            data_source=DEFAULT_DATA_SOURCE,
            start_date=start_plus_week.__str__(),
            end_date=end_date.__str__()
        )

        custom_str = fund.get_custom_range_performance(
            start_date.__str__(),
            end_date.__str__()
        )

        log.debug(f'Custom range performance ({symbol}) complete.')

        return custom_str

    def add_fund(self, symbol, name=None):
        """Add fund to saved data.

        Args:
            symbol (str): First parameter. Fund symbol. ex. 'FXAIX' or 'F'. Will
                convert symbol to upper case.
            name (str): Second parameter. OPTIONAL. An unofficial unique
                identifying name chosen by user to represent fund.

        Returns:
            fund (True): True if successful, False otherwise.
        """

        log.debug(f'Add fund using symbol: {symbol}, name: {name}...')

        # Instantiate Fund object.
        fund = self.instantiate_fund(symbol=symbol.upper(), name=name)

        # Add fund to list of funds.
        self.funds.append(fund)

        log.debug(f'Add fund ({fund}) complete.')

        return fund

    def main_event_loop(self):
        """Run application.

        Provides a user-friendly interaction with program from shell. Program
        stays running until user quits.

        Args:
            None

        Returns:
            None
        """

        log.debug('Main Event Loop...')

        log.debug('Main Event Loop complete.')

        return

    def print_to_screen(self, anything):
        """Print any string to screen.

        Args:
            anything (str): String in which to print to screen.

        Returns:
            None
        """

        log.debug('Print to screen...')

        print(anything)

        log.debug('Print to screen complete.')

        return


def parse_args(argv=sys.argv):
    """Setup shell environment to run program."""

    log.debug('Parse_args...')

    # Program description.
    parser = argparse.ArgumentParser(
        description='Description for program.',
        epilog=''
    )

    # What this argument will do.
    parser.add_argument(
        '-t',
        '--test',
        help='Run testing on application and exit',
        action='store_true',
        default=False
    )

    parser.add_argument(
        '-ga',
        '--getall',
        help='Get performance data for all saved funds and exit.',
        action='store_true',
        default=False
    )

    parser.add_argument(
        '-a',
        '--add',
        help='Add fund. Symbol followed by optional Name in quotations.',
        nargs='+',
        metavar=('Symbol', 'Name'),
        default=(None, None)
    )

    parser.add_argument(
        '-d',
        '--delete',
        help='Delete fund. Give symbol for fund to delete.',
        nargs=1,
        default=False,
        metavar='Symbol'
    )

    parser.add_argument(
        '-c',
        '--custom',
        help='Get price difference for fund between date range. Date: (yyyy-mm-dd)',
        nargs=3,
        default=False,
        metavar=('Symbol', 'Start date', 'End date'),
    )

    args = parser.parse_args()  # Collect arguments.

    log.debug(f'Parse_args complete. Args: {args}')

    return args


def run_application(args):
    """Run application based on shell commands.

    Args:
        args (List [args]): List of arguments from argument parser.

    Returns:
        None
    """

    log.debug('Run application...')

    # Skip instantiating Application if self testing is selected.
    if args.test:
        self_test()
        controller_for_yf_self_test()
        pull_from_yf_self_test()
        storage_self_test()
        core_self_test()
        return

    ft = FundTracker()  # Begin application instance.

    if args.getall:
        funds = ft.generate_all_fund_perf_str()
        ft.print_to_screen(funds)
        return

    elif args.add[0] is not None:
        if len(args.add) == 1:  # When name is not collected.
            args.add.append(None)
        ft.add_fund(args.add[0], args.add[1])
        ft.save()
        return

    elif args.delete:
        ft.delete_fund(*args.delete)
        ft.save()
        return

    elif args.custom:
        ft.print_to_screen(ft.custom_range_performance(*args.custom))
        return

    # Run Application main event loop when no args are True.
    ft.main_event_loop()

    log.debug('Run application complete.')

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

    log.debug('Self test...')

    # Conduct unittest.
    suite = unittest.TestLoader().loadTestsFromModule(test_financeapp)
    unittest.TextTestRunner(verbosity=2).run(suite)

    log.debug('Self test complete.')


def test():
    """For development level module testing."""




def main():
    # Configure Rotating Log.
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

    log.debug('main...')

    start_time = time.perf_counter()  # Set initial time to time operations.

    args = parse_args()
    run_application(args)

    end_time = time.perf_counter()  # Set end time for timing operations.
    total_time = round(end_time - start_time, 2)

    log.debug(f'main completed in {total_time} seconds.')


if __name__ == '__main__':
    main()
