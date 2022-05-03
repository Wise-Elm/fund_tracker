#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Author:
    Graham Steeds

Context:
    Provide extended threading functionality.

Description:
    Construct child class (ReturnThreadValue) of threading.Thread so that the thread
    returns the return value from the target function.

    For complete list of arguments and attributes please refer to threading.Thread
    documentation.

Composition Attributes:
    Line length = 88 characters.
"""


import logging
import threading
import uuid
from logging import handlers

DEFAULT_LOG_FILENAME = 'customthread.log'
DEFAULT_LOG_LEVEL = logging.WARNING
RUNTIME_ID = uuid.uuid4()


# Configure logging.
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class CustomThreadError(RuntimeError):
    """Base class for exceptions arising from this module."""


class RTV(threading.Thread):
    """Child class of threading.Thread.

    Constructed to provide a return value to parent.join() for thread of self.

    self.return is the return value from the called function or method.
    self.thread_name is an easily understandable name for the thread intended to be
        used in logging and debugging.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.result = None  # Add self.result for return value.
        self.thread_name = 'Thread-{}'.format(kwargs['args'][0])

        log.debug(f'Initializing {self.thread_name}...')

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
            CustomThreadError (Exception): Raised when self._target (function to be
                called) is not found.
        """

        log.debug(f'{self.thread_name}.run()')

        if self._target is not None:
            # Identify return value for target function.
            self.result = self._target(*self._args, **self._kwargs)
        else:
            msg = f'Target function for Thread-{self.name} not found.'
            log.warning(msg)
            raise CustomThreadError(msg)

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

        log.debug(f'{self.thread_name}.join()')

        super().join(*args, **kwargs)
        return self.result


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