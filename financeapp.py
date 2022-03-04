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
from datetime import datetime, timedelta
from logging import handlers

from core import Fund, DATE_FORMAT
from pull_data import get_fund_data, get_custom_fund_data
from storage import Repo


DEFAULT_LOG_FILENAME = 'financeapp.log'
DEFAULT_LOG_LEVEL = logging.DEBUG
RUNTIME_ID = uuid.uuid4()


# Configure logging.
log = logging.getLogger()
log.addHandler(logging.NullHandler())


class FundTrackerApplicationError(RuntimeError):
    """Base class for exceptions arising from this module."""


class FundTracker:
    """Application for tracking and displaying stock market data.

    Args:
        load (bool): First parameter. Defaults to True. True will load stored
            program data.
        data_file (bool(False) or str): Second parameter. Defaults to False.
            False will signal program to use a default file path for saving
            data. String will signal program to save and retrieve date from
            given path.
    """

    def __init__(self, load=True, data_file=None):
        self.repo = Repo(load, data_file)
        self.symbols_names: list[str] = self.repo.symbols_names  # ex: ['F', 'FXAIX']
        self.funds: list[Fund] = []  # ex: [Fund objects]
        self.instantiate_funds()

    def instantiate_funds(self):
        """Populate self.funds by getting fund data and instantiating Fund
        objects.

        Args:
            None

        Returns:
            self.funds (List[Fund]): List of instantiated Fund objects.
        """

        symbols_names = self.symbols_names or None
        if symbols_names:
            for symbol_name in symbols_names:
                data = get_fund_data(symbol_name[0])
                if not data:
                    continue
                fund_data = self.parse_fund_data(data)
                if not fund_data:
                    continue
                if len(symbol_name) > 1:
                    fund_data.append(symbol_name[1])
                fund = Fund(*fund_data)
                self.funds.append(fund)
        return self.funds

    def parse_fund_data(self, data: dict):
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

        key = tuple(data.keys())
        symbol = key[0]
        currency = data[symbol]['currency']
        instrument_type = data[symbol]['instrumentType']
        all_dates_prices = data[symbol]['prices']
        dates_prices = \
            [[day['formatted_date'], day['close']] for day in all_dates_prices]

        desired_data = [symbol, currency, instrument_type, dates_prices]
        return None or desired_data

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

        if not data:
            data = self.funds
        self.repo.save(data, data_file)

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

        all_performance = ''
        for fund in self.funds:
            all_performance += '\n' + self.generate_fund_performance_str(fund)
            all_performance += '\n' + '*' * 50
        return all_performance

    def generate_fund_performance_str(self, fund: Fund, day=True, week=True, year=True):
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

        return performance

    def custom_range_performance(self, fund: str, start_date, end_date):
        """Get the performance of fund over a specified date range.

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

        # Change start_date and end_date from strings to datetime objects to
        # enable date range comparisons.
        start_date = datetime.strptime(start_date, DATE_FORMAT).date()
        end_date = datetime.strptime(end_date, DATE_FORMAT).date()

        start_date_price = None  # Later populated with float.
        end_date_price = None  # Later populated with float.
        target_fund = None  # Later populated with Fund object.

        # See if fund is already an object.
        if fund in self.funds:
            target_fund = self.funds[self.funds.index(fund)]
            most_current_date = target_fund.dates_prices[0][0]

            # Use last available trading date if end date is past the most
            # current data.
            if end_date >= most_current_date or not end_date:
                end_date_price = most_current_date

            # Pull start_date_price from stored data if date is stored.
            if start_date > target_fund.dates_prices[:-1][0][0]:
                for date_price in target_fund.dates_prices:
                    if date_price[0] == start_date:
                        start_date_price = target_fund.dates_prices

        # When start_date_price is None then retrieve needed data using
        # the pull_data module.
        if start_date_price is None:
            data = get_custom_fund_data(fund, start_date, end_date)
            parsed_data = self.parse_fund_data(data)
            target_fund = Fund(*parsed_data)  # create Fund w/date from desired range.
            start_date_price = target_fund.dates_prices[-1][1]
            end_date_price = target_fund.dates_prices[0][1]

        difference = self.calculate_percentage(start_date_price, end_date_price)
        return difference, start_date, end_date, fund

    def day_performance(self, fund: Fund):
        """Get the performance of fund period between last open and close.

        Args:
            fund (Fund): Fund object.

        Returns:
            tuple(difference[float], Fund): tuple[0] returns the difference in
            closing fund price. tuple[1] returns the Fund object.
        """

        most_current = fund.dates_prices[-1]

        if most_current[1] is None:
            most_current = fund.dates_prices[-2]

        day_before = None
        latest_date = most_current[0]
        day_ago_price = latest_date - timedelta(days=1)

        for date_price in fund.dates_prices:
            if date_price[0] == day_ago_price:
                day_before = date_price

        if day_before:
            difference = self.calculate_percentage(day_before[1], most_current[1])
        else:
            difference = None

        return difference, fund

    def week_performance(self, fund: Fund):
        """Get the performance of fund period between last close and the close
        from a week prior.

        Args:
            fund (Fund): Fund object.

        Returns:
            tuple(difference[float], Fund): tuple[0] returns the difference in
            closing fund price. tuple[1] returns the Fund object.
        """

        most_current = fund.dates_prices[-1]

        if most_current[1] is None:
            most_current = fund.dates_prices[-2]

        week_before = None
        latest_date = most_current[0]
        week_ago_date = latest_date - timedelta(weeks=1)

        for date_price in fund.dates_prices:
            if date_price[0] == week_ago_date:
                week_before = date_price

        if week_before:
            difference = self.calculate_percentage(week_before[1], most_current[1])
        else:
            difference = None

        return difference, fund

    def year_performance(self, fund: Fund):
        """Get the performance of fund period between last close and the close
        from a year prior.

        Args:
            fund (Fund): Fund object.

        Returns:
            tuple(difference[float], Fund): tuple[0] returns the difference in
            closing fund price. tuple[1] returns the Fund object.
        """

        most_current = fund.dates_prices[-1]

        if most_current[1] is None:
            most_current = fund.dates_prices[-2]

        year_before = None
        latest_date = most_current[0]
        year_ago_date = latest_date - timedelta(weeks=52)  # 52 weeks is 1 year.

        for date_price in fund.dates_prices:
            if date_price[0] == year_ago_date:
                year_before = date_price

        if year_before:
            difference = self.calculate_percentage(year_before[1], most_current[1])
        else:
            difference = None

        return difference, fund

    def calculate_percentage(self, first_price: float, last_price: float):
        """Find percentage difference between two numbers. Return is negative
        when first argument is greater than second argument.

        Args:
            first_price (float): First parameter.
            last_price (float): Second parameter.

        Returns:
            difference (float): Percentage difference between first and second
                argument.
        """

        first_price, last_price = float(first_price), float(last_price)

        if first_price == last_price:
            difference = 0.0
        elif first_price > last_price:  # Percentage decrease.
            difference = ((first_price - last_price) / first_price * 100)
            difference = -abs(difference)
        elif first_price < last_price:  # Percentage increase.
            difference = (last_price - first_price) / last_price * 100

        return difference

    def main_event_loop(self):
        """Run application.

        Provides a user-friendly interaction with program from shell. Program
        stays running until user quits.

        Args:
            None

        Returns:
            None
        """

        log.debug('Entering Main Event Loop...')

        pass

        log.debug('Main Event Loop has ended.')

        return

    def print_to_screen(self, anything: str):
        """Print any string to screen.

        Args:
            anything (str): String in which to print to screen.
        """

        print(anything)


def parse_args(argv=sys.argv):
    """Setup shell environment to run program."""

    log.debug('parse_args...')

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

    args = parser.parse_args()  # Collect arguments.

    log.debug(f'args: {args}')
    log.debug('parse_args complete.')

    return args


def run_application(args):
    """Run application based on shell commands.

    Args:
        args (List [args]): List of arguments from argument parser.

    Returns:
        None
    """

    log.debug(args)

    # Skip instantiating Application if self testing is selected.
    if args.test:
        log.debug('Begin unittests...')

        self_test()  # Test application.py

        log.debug('Unittests complete.')

        return

    ft = FundTracker()  # Begin application instance.
    ft.instantiate_funds()
    log.debug('Application instantiated.')

    if args.getall:
        funds = ft.generate_all_fund_perf_str()
        ft.print_to_screen(funds)
        return

    # Run Application main event loop when no args are True.
    ft.main_event_loop()
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

    # Conduct unittest.
    suite = unittest.TestLoader().loadTestsFromModule(test_financeapp)
    unittest.TextTestRunner(verbosity=2).run(suite)


def test():
    """For development level module testing."""

    ft = FundTracker()
    print(ft.generate_all_fund_perf_str())
    ft.save()


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
    # main()
    test()


