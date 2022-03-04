#!/usr/bin/python
# -*- coding: utf-8 -*-


import logging
import uuid
from datetime import datetime
from logging import handlers


DATE_FORMAT = '%Y-%m-%d'
DEFAULT_CORE_LOG_FILENAME = 'core.log'  # Used when __name__ == '__main__'
CORE_LOG_LEVEL = logging.WARNING
RUNTIME_ID = uuid.uuid4()

# Configure logging.
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class CoreError(RuntimeError):
    """Base class for exceptions arising from this module."""


class Fund:

    def __init__(self, symbol, currency, instrument_type, dates_prices, name=None):
        self.name = name
        self.symbol = symbol
        self.currency = currency
        self.instrument_type = instrument_type
        for dp in dates_prices:
            dp[0] = datetime.strptime(dp[0], DATE_FORMAT).date()
        self.dates_prices = dates_prices

    def __str__(self):
        blank = ''
        formatted_price = '{:.2f}'.format(self.dates_prices[-1][1])
        formatted_str = \
            f'{self.symbol} - {self.name or blank}\n' \
            f'{self.currency} - {self.instrument_type}\n' \
            f'Latest price: {self.dates_prices[-1][0]} - ${formatted_price}'
        return formatted_str

    def __repr__(self):
        return self.symbol

    def __eq__(self, other):
        if other is type(Fund):
            return True if self.symbol == other.symbol else False
        elif isinstance(other, str):
            return True if self.symbol == other else False


def self_test():
    """Run Unittests on module.

    Args:
        None

    Returns:
        None
    """

    import unittest

    import test_core

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
