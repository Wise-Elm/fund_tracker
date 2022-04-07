#!/usr/bin/env python
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
            (ex. [[2021-03-09, 166.02999877929688], [[2021-03-10, 164.02999877929688]]], 
            where the list is ordered by date, the most current date being list[:-1].)
            
    When these parameters are met financeapp can work with any outside data gathering 
    module.

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
"""

import argparse
import logging
import sys
import time
import uuid
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from logging import handlers

# Local imports.
from core import core_self_test, Fund
from controller_for_yf import get_yf_fund_data, controller_for_yf_self_test
from customthread import ReturnThreadValue as RTV
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

        # Use custom thread class (RTV) to get return values from called method.
        # Construct list of thread objects.
        threads = [RTV(target=self.instantiate_fund,
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

            thread = RTV(target=source_method, args=[symbol])
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
            all_performance += '\n' + self.generate_fund_performance_str(fund, *kvargs)
            all_performance += '\n' + '*' * 50

        log.debug('Generate all fund perf str complete.')

        return all_performance

    def generate_fund_performance_str(self, fund, day=True, week=True, year=True):
        """Generates previous 24 hour, week, and year performance of fund
        depending on arguments.

        Args:
            fund (Fund): Fund object.
            day (Bool): Defaults to True. When true includes previous day fund
                performance in return.
            week (Bool): Defaults to True. When true includes previous week
                fund performance in return.
            year (Bool): Defaults to True. When true includes previous year
                fund performance in return.

        Returns:
            performance (str): String including general fund information as
                well time based performance data depending on arguments.
        """

        log.debug(f'Generate fund perf str ({fund.__repr__()})...')

        performance = fund.__str__()

        if day:
            day_change = '{:.2f}'.format(self.day_performance(fund)[0])
            if day_change[0] != '-':  # Add '+' when number is not negative.
                day_change = '+' + day_change
            performance += '\n' + f'Previous 24 hours: {day_change}%'

        if week:
            week_change = '{:.2f}'.format(self.week_performance(fund)[0])
            if week_change[0] != '-':  # Add '+' when number is not negative.
                week_change = '+' + week_change
            performance += '\n' + f'Previous week: {week_change}%'

        if year:
            year_change = '{:.2f}'.format(self.year_performance(fund)[0])
            if year_change[0] != '-':  # Add '+' when number is not negative.
                year_change = '+' + year_change
            performance += '\n' + f'Previous year: {year_change}%'

        log.debug(f'Generate fund perf str ({fund.__repr__()}) complete.')

        return performance

    def custom_range_performance(self, fund, start_date, end_date):
        """Get the performance of a fund over a specified date range.

        Args:
            fund (str): Fund symbol:
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

        log.debug(f'Custom range performance ({fund})...')

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

        # Include an additional month before the start date to make up for dates where
        # pricing and/or dates are not available.
        start_plus_month = start_date - relativedelta(months=1)

        custom_data = self.pull_yahoofinancial(fund,
                                               start_plus_month.__str__(),
                                               end_date.__str__())

        # Replace date_price list in custom_date so that the first item in the list
        # is the best usable start date, and the last item in the list is the best
        # usable end date.
        custom_data[3] = self.get_closest_dates(custom_data[3], start_date, end_date)

        # Instantiate as fund object.
        fund = Fund(*custom_data)

        # Get dates and prices for comparison.
        oldest_price, newest_price = fund.dates_prices[0][1], fund.dates_prices[-1][1]

        # Get percentage difference between first and last dates.
        difference = self.calculate_percentage(oldest_price, newest_price)

        msg = fund.__str__() + '\nPerformance between {} and {}: ' \
                               '{:.2f}%.'.format(start_date, end_date, difference)

        log.debug(f'Custom range performance ({fund}) complete.')

        return msg

    def get_closest_dates(self, dates_prices, start_date, end_date):
        """Finds the closest valid dates on or before argument dates.

         Will view a date as invalid if it is after the argument date or if it contains
         pricing information of None.

         Args:
             dates_prices (list[date(str), price(str)]): First parameter. List of dates
                and prices.
             start_date (datetime obj): Second parameter. Ideal starting date.
             end_date (datetime obj): Thirt parameter. Idea ending date.

         Returns:
             dates_prices (list[date(str), price(str)]): List of dates and associated
                prices where the first and last items best fit the start_date and
                end_date arguments respectively.
         """

        log.debug(f'Finding closest dates for start date ({start_date.__str__()}), and '
                  f'end date ({end_date.__str__()})...')

        # Find an end date on or before the requested end date that has both date and
        # price information.
        end_found = False
        while not end_found:
            if datetime.strptime(dates_prices[-1][0], DATE_FORMAT).date() > end_date:
                dates_prices.pop()
                continue
            elif dates_prices[-1][1] is None:
                dates_prices.pop()
            else:
                end_found = True

        # Find a start date on or before the requested start date that has both date and
        # price information.

        # Find index of start date in dates_prices or closest dates before is start date
        # does not exist.
        start_index = 0
        while datetime.strptime(dates_prices[start_index][0], DATE_FORMAT).date() < \
            start_date:
            start_index += 1

        start_found = False
        while not start_found:
            if dates_prices[start_index][1] is None:
                start_index -= 1
            else:
                start_found = True

        # Eliminate dates outside desired ranges as they are unneeded.
        dates_prices = dates_prices[start_index:]

        log.debug(f'Closest date to start date ({start_date.__str__()} --> '
                  f'{dates_prices[0][0]}), and end date ({end_date.__str__()}, '
                  f'{dates_prices[-1][0]}) found.')

        return dates_prices

    def day_performance(self, fund):
        """Get the performance of fund period between last open and close.

        Args:
            fund (Fund): Fund object.

        Returns:
            tuple(difference[float], Fund): tuple[0] returns the difference in
            closing fund price. tuple[1] returns the Fund object.
        """

        log.debug(f'Day performance ({fund.__repr__()})...')

        # Get most current date with price data.
        most_current_date_price = self.get_most_current_price(fund)
        most_current_date = most_current_date_price[0]
        most_current_price = most_current_date_price[1]

        # Find the day before the latest price.
        day_before = most_current_date - timedelta(days=1)

        # Get the closest date with date and price data before the most_current_date.
        day_before_date_price = self.get_most_current_price(fund, day_before)
        day_before_price = day_before_date_price[1]

        # Calculate percentage difference in prices.
        difference = self.calculate_percentage(day_before_price, most_current_price)

        log.debug(f'Day performance ('
                  f'fund: {fund.__repr__()}, performance: {difference})'
                  f' complete.')

        return difference, fund

    def week_performance(self, fund):
        """Get the performance of fund period between last close and the close
        from a week prior.

        Args:
            fund (Fund): Fund object.

        Returns:
            tuple(difference[float], Fund): tuple[0] returns the difference in
            closing fund price. tuple[1] returns the Fund object.
        """

        log.debug(f'Week performance ({fund.__repr__()})...')

        # Get most current date with price data.
        most_current_date_price = self.get_most_current_price(fund)
        most_current_date = most_current_date_price[0]
        most_current_price = most_current_date_price[1]

        # Find the week before the latest price.
        day_before = most_current_date - timedelta(weeks=1)

        # Get the closest date with date and price data before the most_current_date.
        day_before_date_price = self.get_most_current_price(fund, day_before)
        day_before_price = day_before_date_price[1]

        # Calculate percentage difference in prices.
        difference = self.calculate_percentage(day_before_price, most_current_price)

        log.debug(f'Week performance ('
                  f'fund: {fund.__repr__()}, performance: {difference})'
                  f' complete.')

        return difference, fund

    def year_performance(self, fund):
        """Get the performance of fund period between last close and the close
        from a year prior.

        Args:
            fund (Fund): Fund object.

        Returns:
            tuple(difference[float], Fund): tuple[0] returns the difference in
            closing fund price. tuple[1] returns the Fund object.
        """

        log.debug(f'Year performance ({fund.__repr__()})...')

        # Get most current date with price data.
        most_current_date_price = self.get_most_current_price(fund)
        most_current_date = most_current_date_price[0]
        most_current_price = most_current_date_price[1]

        # Find the year before the latest price.
        day_before = most_current_date - timedelta(weeks=52)

        # Get the closest date with date and price data before the most_current_date.
        day_before_date_price = self.get_most_current_price(fund, day_before)
        day_before_price = day_before_date_price[1]

        # Calculate percentage difference in prices.
        difference = self.calculate_percentage(day_before_price, most_current_price)

        log.debug(f'Year performance ('
                  f'fund: {fund.__repr__()}, performance: {difference})'
                  f' complete.')

        return difference, fund

    def get_most_current_price(self, fund, search_date=None):
        """Get most current price for a Fund.

        The most current price will not necessarily be the last trading day as some
        pricing information lags behind the market close.

        Args:
            fund (Fund obj): Fund object.
            search_date (datetime obj): OPTIONAL. Defaults to today's date. Datetime
            object representing date. Will search for the closest date before argument
            date.
                    Example:
                        Program will start searching for date and price information
                        starting with argument date, and proceed to earlier dates
                        progressively until date is found with both date and price
                        information.

        Returns:
            tuple(most_current_date, most_current_date): The most current date and
                price information available.
        """

        log.debug(f'Get most current price: ({fund.__repr__()})...')

        # Use latest date in fund as a default.
        if search_date is None:
            search_date = fund.dates_prices[-1][0]

        # Find index of search_date in fund.dates_prices.
        index = len(fund.dates_prices) - 1
        date_found = False
        while not date_found:
            for date_, price in reversed(fund.dates_prices):
                # If search date not available get the closest date before .
                if date_ == search_date or date_ < search_date:
                    date_found = True
                    break
                else:
                    index -= 1

        # Get date and price data for search_date argument.
        most_current_date, most_current_price = \
            fund.dates_prices[index][0], fund.dates_prices[index][1] or None

        # Revert to previous day if price data has not been updated.
        while most_current_price is None:
            for date_, price in reversed(fund.dates_prices):
                most_current_date = date_  # ex. datetime.date(2022, 3, 16)
                most_current_price = price  # ex.151.123456789

        log.debug(f'Get most current price ({fund.__repr__()}, '
                  f'price: {most_current_price}, date: {most_current_date}) complete. ')

        return most_current_date, most_current_price

    def calculate_percentage(self, first_price, last_price):
        """Find percentage difference between two numbers. Return is negative
        when first argument is greater than second argument.

        Args:
            first_price (float): First parameter.
            last_price (float): Second parameter.

        Returns:
            difference (float): Percentage difference between first and second
                argument.
        """

        log.debug(f'Calculate percentage (num1: {first_price}, num2: {last_price})...')

        first_price, last_price = float(first_price), float(last_price)

        if first_price == last_price:
            difference = 0.0
        elif first_price > last_price:  # Percentage decrease.
            difference = ((first_price - last_price) / first_price * 100)
            difference = -abs(difference)
        elif first_price < last_price:  # Percentage increase.
            difference = (last_price - first_price) / last_price * 100

        log.debug(f'Calculate percentage (percentage: {difference}) complete.')

        return difference

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

    pass


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
