#!/usr/bin/env python
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
from datetime import date, datetime, timedelta
from logging import handlers

from core import Fund, DATE_FORMAT
from controller_for_yf import get_yf_fund_data
from storage import Repo

DEFAULT_DATA_FILE = 'data.csv'
DEFAULT_LOG_FILENAME = 'financeapp.log'
DEFAULT_LOG_LEVEL = logging.DEBUG
DEFAULT_DATA_SOURCE = 'yahoofinance'
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
            modules for retrieving fund data.

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
        
        log.debug(f'Instantiate saved funds. Data source: {data_source}...')

        instantiated_funds = []  # List of Fund objects.

        # Instantiate each saved fund and
        for symbol_name in self.symbols_names:
            fund = self.instantiate_fund(*symbol_name)
            instantiated_funds.append(fund)
        
        log.debug('Instantiate saved funds complete.')
        
        return instantiated_funds

    def instantiate_fund(self, symbol, name=None, data_source=DEFAULT_DATA_SOURCE):
        """Instantiate a Fund object.

        Uses self.check_data_source() to confirm legality of data_source argument.

        Args:
            symbol (str): Symbol representing a fund. ex 'FXAIX'.
            name (str or None): OPTIONAL. Defaults to None. A customizable name for
                fund.
            data_source (str): OPTIONAL. Defaults to a usable data source. A module from
                which to pull fund data.

        Returns:
            (fund or None): fund when data_source is legal, and fund is found matching
                the symbol parameter. None when an error occurs.
        """

        log.debug(f'Instantiate fund using symbol: {symbol}, name: {name}, '
                  f'data_source: {data_source}...')

        try:
            # Will raise exception if data_source is not legal.
            self.check_data_source(data_source)

        except FundTrackerApplicationError:
            return None

        finally:
            # Identify method connecting to external module for pulling data.
            source_method = self.AVAILABLE_DATA_SOURCES[data_source]

            data = source_method(symbol)  # Get fund data from source method.
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

    def pull_yahoofinancial(self, symbol):
        """Get fund data from yahoofinancial module.

        Args:
            symbol (str): Symbol of fund on which to pull data. Ex: FXAIX.

        Returns:
            data (list[symbol, denomination, type, list[[date, price]]]):
                List of fund data.
        """

        log.debug(f'Pulling data for fund ({symbol}) from yahoofinancial...')

        data = get_yf_fund_data(symbol)

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

    # TODO (GS): Fix this method.
    # def custom_range_performance(self, fund, start_date, end_date):
    #     """Get the performance of fund over a specified date range.
    #
    #     Args:
    #         fund (str): Fund symbol:
    #             Example:
    #                 'FXAIX'
    #         start_date (str): Date in format yyyy-mm-dd.
    #         end_date (str): Date in format yyyy-mm-dd.
    #
    #     Returns:
    #         tuple(
    #             difference:float,
    #             start_date:datetime object,
    #             end_date:datetime object,
    #             fund:Fund object
    #         )
    #     """
    #
    #     log.debug(f'Custom range performance ({fund})...')
    #
    #     # Change start_date and end_date from strings to datetime objects to
    #     # enable date range comparisons.
    #     start_date = datetime.strptime(start_date, DATE_FORMAT).date()
    #     end_date = datetime.strptime(end_date, DATE_FORMAT).date()
    #
    #     start_date_price = None  # Later populated with float.
    #     end_date_price = None  # Later populated with float.
    #     target_fund = None  # Later populated with Fund object.
    #
    #     # See if fund is already an object.
    #     if fund in self.funds:
    #         target_fund = self.funds[self.funds.index(fund)]
    #         most_current_date = target_fund.dates_prices[0][0]
    #
    #         # Use last available trading date if end date is past the most
    #         # current data.
    #         if end_date >= most_current_date or not end_date:
    #             end_date_price = most_current_date
    #
    #         # Pull start_date_price from stored data if date is stored.
    #         if start_date > target_fund.dates_prices[:-1][0][0]:
    #             for date_price in target_fund.dates_prices:
    #                 if date_price[0] == start_date:
    #                     start_date_price = target_fund.dates_prices
    #
    #     # When start_date_price is None then retrieve needed data using
    #     # the pull_data module.
    #     if start_date_price is None:
    #         data = get_custom_fund_data(fund, start_date, end_date)
    #         parsed_data = self.parse_fund_data(data)
    #         target_fund = Fund(*parsed_data)  # create Fund w/date from desired range.
    #         start_date_price = target_fund.dates_prices[-1][1]
    #         end_date_price = target_fund.dates_prices[0][1]
    #
    #     difference = self.calculate_percentage(start_date_price, end_date_price)
    #
    #     log.debug(f'Custom range performance ({fund}) complete.')
    #
    #     return difference, start_date, end_date, fund

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
                if date_ == search_date:
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

        fund = self.instantiate_fund(symbol=symbol.upper(), name=name)

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

    # Run Application main event loop when no args are True.
    ft.main_event_loop()
    ft.save()

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

    ft = FundTracker()
    funds = ft.generate_all_fund_perf_str()
    print(funds)


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
    main()
    # test()