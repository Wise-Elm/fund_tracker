#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Author:
    Graham Steeds

Context:
    This module provides  the Fund object class for fund_tracker.py. The Fund object
    class represents a financial instrument such as a mutual fund or stock, that is
    traded in a financial market.

Attributes:
    CORE_LOG_LEVEL: Default log level when this module is called directly.
    DATE_FORMAT: Format for working with dates. (yyyy-mm-dd).
    DEFAULT_CORE_LOG_FILENAME: Default filename for logging when module called directly.
    RUNTIME_ID: Generate a unique uuid object. Used in logging.

Composition Attributes:
    Line length = 88 characters.
"""

import bisect
import logging
import uuid
from datetime import date, datetime, timedelta
from logging import handlers


CORE_LOG_LEVEL = logging.WARNING
DATE_FORMAT = '%Y-%m-%d'
DEFAULT_CORE_LOG_FILENAME = 'core.log'  # Used when __name__ == '__main__'
RUNTIME_ID = uuid.uuid4()

# Configure logging.
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class CoreError(RuntimeError):
    """Base class for exceptions arising from this module."""


class Fund:
    """Represents a financial instrument such as a mutual fund or stock.

    Args:
        symbol (str): First parameter. Symbol representing a financial
            instrument, such as 'F'.
        currency (str): Second parameter. Symbol of trading currency such as 'USD'.
        instrument_type (str): Third parameter. Type of fund. Example: 'MUTUALFUND' or
            'STOCK'.
        dates_prices (list[['yyyy-mm-dd', 'float']]): Fourth parameter. List of lists
            containing date and price data.
        name (str): OPTIONAL. An optional given name or nickname for fund by user.
    """

    def __init__(self, symbol, currency, instrument_type, dates_prices, name=None):
        self.symbol = symbol.upper()  # Fund symbol. Ex. 'FXAIX'.
        self.currency = currency.upper()  # Currency of fund. Ex. 'USD'.
        self.instrument_type = instrument_type.upper()  # Ex. 'STOCK'.
        # Turn date string into datetime object in yyyy-mm-dd format.
        self.dates_prices = [[datetime.strptime(dp[0], DATE_FORMAT).date(), dp[1]]
                             for dp in dates_prices]
        self.name = name  # Optional name for fund given by user.

    def __str__(self):
        """String representation of Fund.

        Args:
            None

        Returns:
            formatted_str (str): String representing Fund.
                Example:
                    'FSMAX -\nUSD - MUTUALFUND\nLatest price: 2022-04-05 - $78.42'
        """

        log.debug(f'__str__ ({self.__repr__()})...')

        # Get the latest price and round it to 2 decimal places.
        if self.dates_prices[-1][1]:
            formatted_price = '{:.2f}'.format(self.dates_prices[-1][1])
        else:  # Use previous days data when latest data is not available.
            formatted_price = '{:.2f}'.format(self.dates_prices[-2][1])

        formatted_str = '{} - {}\n{} - {}\nLatest price: {} - ${}'.\
            format(
                self.symbol,
                self.name or '',
                self.currency,
                self.instrument_type,
                self.dates_prices[-1][0],
                formatted_price
            )

        log.debug(f'__str__ ({self.__repr__()}) complete...')

        return formatted_str

    def __repr__(self):
        """String of funds unique identifying trait: self.symbol.

        Args:
            None

        Returns:
            self.symbol (str): The symbol for the Fund.
        """

        log.debug(f'__repr__ ({self.symbol}) complete.')

        return self.symbol

    def __eq__(self, other):
        """Determine the equality of self and other.

        Other can be a Fund object or a string representing a fund symbol.

        Args:
            other (Fund obj, OR str): Determine the equality of self and other based on
            if Fund.symbol == other.symbol, or if Fund.symbol == other.

        Returns:
            True if found to be the same, False otherwise.
        """

        log.debug(f'__eq__ (self: {self.__repr__()}, other: {other})...')

        if isinstance(other, Fund):  # Compare if type(other) is Fund.
            log.debug(f'__eq__ (other type = {type(other)}, '
                      f'self is other = '
                      f'{True if self.symbol == other.symbol else False}')
            return True if self.symbol == other.symbol else False

        elif isinstance(other, str):  # Compare if type(other) is str.
            log.debug(f'__eq__ (other type = {type(other)}, '
                      f'self is other = '
                      f'{True if self.symbol == other else False}')
            return True if self.symbol == other else False

        else:  # When type other is not a legal type. i.e. a Fund or str.
            msg = f'Type {type(other)} is not a legally comparable type.'
            log.warning(msg)
            raise CoreError(msg)

    def generate_fund_performance_str(self, day=True, week=True, year=True):
        """Generates previous 24 hour, week, and year performance of fund
        depending on arguments.

        Args:
            day (Bool): Defaults to True. When true includes previous day fund
                performance in return.
            week (Bool): Defaults to True. When true includes previous week
                fund performance in return.
            year (Bool): Defaults to True. When true includes previous year
                fund performance in return.

        Returns:
            performance (str): String including general fund information as
                well time based performance data depending on arguments.

        # TODO (GS): Add graph height and length characteristics to arguments.
        """

        log.debug(f'Generate fund perf str ({self.__repr__()})...')

        performance = '\n' + self.__str__()

        fmt = "\n{:18}: {:+6.2f}"  # shared format string for past performances
        #         msg    value     # + means always include +/- for pos/neg
        # lines up messages and percent changes

        if day:
            performance += fmt.format('Previous 24 hours',
                                      self.day_performance())
        if week:
            performance += fmt.format('Previous week',
                                      self.week_performance())

        if year:
            performance += fmt.format('Previous year',
                                      self.year_performance())

        log.debug(f'Generate fund perf str ({self.__repr__()}) complete.')

        performance += '\n\n' + self.graph()

        return performance

    def graph(self, height=15, length=100):
        """Draw a graph of fund performance over the past 12 months.

        Graph will be plotted with the earliest price first, followed by latest price,
        and filled in with subsequent data as length will allow.

        Args:
            height (int): First parameter. Optional. Height of graph.
            length (int): Second parameter. Optional. Length of graph.

        Returns:
            graph (str): String representation of graph.

        Raises:
            CoreError when height or length is <= 0.
        """

        if height < 1:
            msg = f'Graph height must be greater that 0. Currently height is {height}.'
            log.warning(msg)
            raise CoreError(msg)

        if length < 1:
            msg = f'Graph length must be greater that 0. Currently length is {length}.'
            log.warning(msg)
            raise CoreError(msg)

        # Find most current date and associated price.
        current_date_, current_price = self.get_most_current_price()

        # Find start date based off current_date.
        previous_date_, previous_price = \
            self.get_most_current_price(current_date_ - timedelta(weeks=52))

        # Create new list containing dates and prices between the previous and current
        # dates.
        lst = [dp for dp in self.dates_prices if
               previous_date_ <= dp[0] <= current_date_]

        # Confirm that lst is in order from least to greatest date.
        # (oldest to most recent)
        lst.sort(key=lambda date_price: date_price[0])

        # List of data matching the length argument.
        data = self._trim_list(lst, length)

        # Find highest and lowest price, as well as the difference between the two.
        highest_price = max(data, key=lambda dp: dp[1])
        lowest_price = min(data, key=lambda dp: dp[1])
        price_difference = highest_price[1] - lowest_price[1]

        # Find pricing difference from one row to another.
        row_price_difference = price_difference / height

        # Modify graph_lst so dates are replaced with row height position.
        for dp in data:
            row_found = False
            graph_row = 0
            price_segment = row_price_difference
            while row_found is False:
                if dp[1] <= price_segment + lowest_price[1]:
                    dp[0] = graph_row
                    row_found = True
                else:
                    graph_row += 1
                    price_segment += row_price_difference

        graph = self._construct_graph(
                    data,
                    height,
                    length,
                    lowest_price,
                    highest_price,
                    previous_date_,
                    current_date_
        )

        return graph

    def _trim_list(self, lst, length):
        """Prepare list for graphing.

        Trims the list of data so that it is the same length as the length argument
        and still represents an accurate cross-section of the data.

        Args:
            lst (list(list(datetime object, price))): Data list.
            length (positive int): Length for graph.

        Returns:
            data (list(list(datetime object, price)): List of data matching the length
                argument and representing a cross-section of the lst argument.
        """

        # Form a list of dates & prices that matches the length argument.
        frequency = len(lst) // length  # Frequency of dates to pick.
        data = []
        for i in lst:
            # Automatically pick first and last dates/prices.
            if lst.index(i) == lst[0] or lst.index(i) == lst[-1]:
                data.append(i)
            # Pick dates/prices that match frequency.
            elif lst.index(i) % frequency == 0:
                data.append(i)

        # Trim length of graph list.
        # If index of last date/price in list % frequency != 0 there will be an extra
        # entry. Trim the middle most date/price.
        while len(data) > length:
            data.pop(len(data) // 2)

        return data

    def _construct_graph(
            self,
            data,
            height,
            length,
            lowest_price,
            highest_price,
            previous_date_,
            current_date_
    ):
        """Construct graph string.

        Helper method for self.graph.

        Args:
            data (list(list(date object, int))): First parameter. List of lists
                containing dates and associated prices.
            height (int): Second parameter. Height of graph.
            length (int): Third parameter. Length of graph.
            lowest_price (list(datetime obj, float)): Fourth parameter. List where
                index 1 indicates the lowest price represented in data.
            highest_price (list(datetime obj, float)): Fifth parameter. List where
                index 1 indicates the highest price represented in data.
            previous_date_ (datetime object): Sixth parameter. Represents the earliest
                date for the graph to plot.
            current_date_ (datetime object): Seventh parameter. Represents the latest
                date for the graph to plot.
        """

        fmt = '{:5.2f}'  # Format for y axis values.
        graph = ''  # String on which the graph is drawn.
        graph_complete = False
        row = height - 1  # Graph row.

        while graph_complete is False:

            # Loop for each graph row.
            for h in range(height):

                # Loop for each data point in graph_lst.
                for data_point in data:
                    # Data point matches price category.
                    if data_point[0] == row:
                        graph += '*'
                    # Data point does not match price category.
                    else:
                        graph += ' '

                # Add the highest price to end of line at top of graph.
                if row == height - 1:
                    graph += '|' + '$' + fmt.format(highest_price[1]) + '\n'
                # Add the lowest price to end of line at bottom of graph.
                elif row == 0:
                    graph += '|' + '$' + fmt.format(lowest_price[1]) + '\n'
                # Rows that are not the top or bottom.
                else:
                    graph += '|\n'
                # Increment row.
                row -= 1

            graph += ('_' * length) + '|'  # Draw x-axis.
            graph_complete = True  # Graph structure complete.

        # Place dates under x axis.
        earliest_date, latest_date = str(previous_date_), str(current_date_)
        # Determine number of blank spaces between dates.
        num_spaces = length - len(earliest_date) - len(latest_date)
        # Construct footer.
        footer = earliest_date + ' ' * num_spaces + latest_date
        # Add footer if there is enough space. Determined by the length of graph.
        if num_spaces > 3:
            graph += '\n' + footer

        return graph

    def day_performance(self):
        """Get the performance of fund period between last open and close.

        Args:
            None

        Returns:
            difference(float): Difference in closing fund price.
        """

        log.debug(f'Day performance ({self.__repr__()})...')

        current_date_, current_price = self.get_most_current_price()
        previous_date_, previous_price = \
            self.get_most_current_price(self.dates_prices[-1][0] - timedelta(days=1))

        difference = calculate_percentage(current_price, previous_price)

        log.debug(f'Day performance ('
                  f'fund: {self.__repr__()}, performance: {difference})'
                  f' complete.')

        return difference

    def week_performance(self):
        """Get the performance of fund period between last close and the close
        from a week prior.

        Args:
            fund (Fund): Fund object.

        Returns:
            tuple(difference[float], Fund): tuple[0] returns the difference in
            closing fund price. tuple[1] returns the Fund object.
        """

        log.debug(f'Week performance ({self.__repr__()})...')

        # Get most current date with price data.
        most_current_date_price = self.get_most_current_price()
        most_current_date = most_current_date_price[0]
        most_current_price = most_current_date_price[1]

        # Find the week before the latest price.
        day_before = most_current_date - timedelta(weeks=1)

        # Get the closest date with date and price data before the most_current_date.
        day_before_date_price = self.get_most_current_price(day_before)
        day_before_price = day_before_date_price[1]

        # Calculate percentage difference in prices.
        difference = calculate_percentage(day_before_price, most_current_price)

        log.debug(f'Week performance ('
                  f'fund: {self.__repr__()}, performance: {difference})'
                  f' complete.')

        return difference

    def year_performance(self):
        """Get the performance of fund period between last close and the close
        from a year prior.

        Args:
            fund (Fund): Fund object.

        Returns:
            tuple(difference[float], Fund): tuple[0] returns the difference in
            closing fund price. tuple[1] returns the Fund object.
        """

        log.debug(f'Year performance ({self.__repr__()})...')

        # Get most current date with price data.
        most_current_date_price = self.get_most_current_price()
        most_current_date = most_current_date_price[0]
        most_current_price = most_current_date_price[1]

        # Find the year before the latest price.
        day_before = most_current_date - timedelta(weeks=52)

        # Get the closest date with date and price data before the most_current_date.
        day_before_date_price = self.get_most_current_price(day_before)
        day_before_price = day_before_date_price[1]

        # Calculate percentage difference in prices.
        difference = calculate_percentage(day_before_price, most_current_price)

        log.debug(f'Year performance ('
                  f'fund: {self.__repr__()}, performance: {difference})'
                  f' complete.')

        return difference

    def get_most_current_price(self, search_date=None):
        """Get most current price for a Fund.

        The most current price will not necessarily be the last trading day as some
        pricing information lags behind the market close and many days, such as
        weekends and holidays, are days without trading.

        Args:
            search_date (datetime obj): OPTIONAL. Defaults to today's date. Datetime
            object representing date. Will search for the closest date before argument
            date.
                    Example:
                        Program will start searching for date and price information
                        starting with argument date, and proceed to earlier dates
                        progressively until date is found with both date and price
                        information.

        Returns:
            tuple(most_current_date, most_current_price): The most current date and
                price information available.
        """

        log.debug(f'Get most current price: ({self.__repr__()})...')

        # Use latest date in fund as a default.
        if search_date is None:
            search_date = self.dates_prices[-1][0]

        # The bisect module provides O(log(N)) searching.
        # Identify index of search_date.
        index = bisect.bisect_left(
            self.dates_prices,  # List[list[date, price]]
            search_date,
            key=(lambda dp: dp[0]))  # Position for date within inner lists.

        # TODO (GS): Check this over.
        # Get date and price data for search_date argument.
        # Revert to previous day if price data has not been updated.
        most_current_price = None
        while most_current_price is None:
            most_current_date, most_current_price = \
                self.dates_prices[index][0], self.dates_prices[index][1] or None
            index -= 1

        log.debug(f'Get most current price ({self.__repr__()}, '
                  f'price: {most_current_price}, date: {most_current_date}) complete. ')

        return most_current_date, most_current_price

    def get_closest_dates(self, start_date, end_date):
        """Finds the closest valid dates on or before argument dates.

         Will view a date as invalid if it is after the argument date or if it contains
         pricing information of None.

         Args:
             start_date (datetime obj): Second parameter. Ideal starting date.
             end_date (datetime obj): Third parameter. Ideal ending date.

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
            if self.dates_prices[-1][0] > end_date:
                self.dates_prices.pop()
                continue
            elif self.dates_prices[-1][1] is None:
                self.dates_prices.pop()
            else:
                end_found = True

        # Find a start date on or before the requested start date that has both date and
        # price information.

        # Find index of start date in dates_prices or closest dates before is start date
        # does not exist.
        start_index = 0
        while self.dates_prices[start_index][0] < start_date:
            start_index += 1

        start_found = False
        while not start_found:
            if self.dates_prices[start_index][1] is None:
                start_index -= 1
            else:
                start_found = True

        # Eliminate dates outside desired ranges as they are unneeded.
        dates_prices = self.dates_prices[start_index:]

        log.debug(f'Closest date to start date ({start_date.__str__()} --> '
                  f'{dates_prices[0][0]}), and end date ({end_date.__str__()}, '
                  f'{dates_prices[-1][0]}) found.')

        return dates_prices

    def get_custom_range_performance(self, start_date, end_date):
        """Generate a string to show fun performance between argument dates.

        Args:
            start_date (str): Date in format yyyy-mm-dd.
            end_date (str): Date in format yyyy-mm-dd.

        Returns:
            custom_str (str): String displaying performance between argument dates.
        """

        log.debug(f'Generating custom range performance between {start_date} and '
                  f'{end_date}...')

        # Convert dates to datetime objects.
        today = date.today()
        start_date = datetime.strptime(start_date, DATE_FORMAT).date()
        end_date = datetime.strptime(end_date, DATE_FORMAT).date()

        # Raise exception if end date is the same or before start date.
        if end_date <= start_date:
            msg = f'Start date({start_date.__str__()}) must be before end date ' \
                  f'({end_date.__str__()}).'
            log.warning(msg)
            raise CoreError(msg)

        # Raise exception if end date is in the future.
        if end_date > today:
            msg = f'End date ({end_date.__str__()}) is out of range (in the future).'
            log.warning(msg)
            raise CoreError(msg)

        # Find best matching dates.
        dates_prices = self.get_closest_dates(start_date, end_date)
        # Locate associated best matching dates.
        oldest_price, newest_price = dates_prices[0][1], dates_prices[-1][1]
        difference = calculate_percentage(oldest_price, newest_price)

        custom_str = self.__str__() + '\nPerformance between {} and {}: ' \
                               '{:.2f}%.'.format(start_date, end_date, difference)

        log.debug(f'Custom range performance string between {start_date} and {end_date} '
                  f'complete.')

        return custom_str


def calculate_percentage(first_price, last_price):
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

    # Solution as suggested by Chris Kauffman, UMN. Original version worked but does
    # not look as clean. Can be found in Git history.
    first_price, last_price = float(first_price), float(last_price)
    big, lil = max(first_price, last_price), min(first_price, last_price)
    # Determine if difference is positive or negative.
    sign = +1 if first_price < last_price else -1
    difference = (big - lil) / big * 100 * sign

    log.debug(f'Calculate percentage (percentage: {difference}) complete.')

    return difference


def core_self_test():
    """Run Unittests on module.

    Args:
        None

    Returns:
        None
    """

    import unittest

    from tests import test_core

    # Conduct unittest.
    suite = unittest.TestLoader().loadTestsFromModule(test_core)
    unittest.TextTestRunner(verbosity=2).run(suite)


def test():
    """For development level module testing."""

    pass


if __name__ == '__main__':

    # Configure Rotating Log. Only runs when module is called directly.
    handler = handlers.RotatingFileHandler(
        filename=DEFAULT_CORE_LOG_FILENAME,
        maxBytes=100**3,  # 0.953674 Megabytes.
        backupCount=1
    )
    formatter = logging.Formatter(
        f'[%(asctime)s] - {RUNTIME_ID} - %(levelname)s - [%(name)s:%(lineno)s] - '
        f'%(message)s'
    )
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.setLevel(CORE_LOG_LEVEL)

    core_self_test()
