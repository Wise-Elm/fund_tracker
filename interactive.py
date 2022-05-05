#! /usr/bin/python3.10
# -*- coding: utf-8 -*-

"""
Author:
    Graham Steeds

Context:
    Provide a simplistic interactive shell interface to Fund Tracker.

Description:
    Interactive mode gives user partial functionality containing the core functionality.

    Interactive mode is run by a main event loop that checks for a kill trigger. When
    a kill trigger is not found between user interactions an input handler accepts user
    inputs and calls appropriate methods.

Action sequence:
    main_event_loop ---> _get_welcome
        <---> _get_user_inputs
                <---> _add    --> _find
                        <---------'
                <---> _delete --> _find
                        <---------'
                <---> _invalid
                <---> _menu
                <---> _show all
                <---> _save
                <---> _quit

Attributes:
    DEFAULT_LOG_FILENAME: Default filename for logging when module called directly.
    DEFAULT_LOG_LEVEL: Default log level when this module is called directly.
    RUNTIME_ID: Generate a unique uuid object. Used in logging.

Composition Attributes:
    Line length = 88 characters.

"""

import logging
import uuid
from logging import handlers

# Local imports.
from fund_tracker import FundTracker

DEFAULT_LOG_FILENAME = 'customthread.log'
DEFAULT_LOG_LEVEL = logging.WARNING
RUNTIME_ID = uuid.uuid4()


# Configure logging.
log = logging.getLogger()
log.addHandler(logging.NullHandler())


class Interactive:

    def __init__(self):

        self.ft = FundTracker()

        self.OPTIONS = {
            'add': self._add,
            'delete': self._delete,
            'menu': self._menu,
            'quit': self._quit,
            'save': self._save,
            'show all': self._show_all,
        }

    def main_event_loop(self):
        """Run application in interactive mode.

        Provides a user-friendly interaction with program from shell. Program stays
        running until user quits.

        Args:
            None

        Returns:
            None
        """

        print(self._get_welcome())  # Print welcome message to screen.

        log.debug('Entering Main Event Loop...')

        run = True
        while run is True:
            result = self._get_user_inputs()
            if result is False:
                run = False

        log.debug('Main Event Loop complete.')

        return

    def _get_user_inputs(self):
        """Handles user inputs.

        Args:
            None

        Returns:
            (False OR None): Returns to _main_event_loop(), False to end program, OR
                None to continue loop.
        """

        log.debug('Prompting user.')

        user_input = input('\nEnter your selection: ')

        if user_input.lower() in self.OPTIONS:  # Check if user input is legal.
            result = self.OPTIONS[user_input.lower()]()
            if result is False:  # Quit main_event_loop and end program.
                return False
            else:
                return True
        else:
            self._invalid()  # Handle indecipherable input.
            return True

    def _get_welcome(self):
        """Display a welcome message and graphic.

        Args:
            None

        Returns:
            welcome (str): Returns welcome message.
        """

        log.debug('Getting welcome...')

        # Welcome graphic formatting.
        ind = 8  # Indent.

        welcome = (
            f"Welcome to:\n" 
            f"{' '* ind} __                __     _____  __    __    __        __   __  \n"
            f"{' '* ind}|__   |  |  |\ |  |  \      |   |__\  |__|  |    |_/  |_   |__\ \n"
            f"{' '* ind}|     |__|  | \|  |__/      |   |  \  |  |  |__  | \  |__  |  \ \n\n"
            "Application is being run in interactive mode. Enter 'menu' for a list of "
            "options, or 'quit' to exit."
        )

        log.debug('Getting welcome complete.')

        return welcome

    def _add(self):
        """Add a new fund.

        Args:
            None

        Returns:
            None
        """

        log.debug('Adding fund...')

        symbol = input('Enter the fund symbol: ')
        symbol = symbol.upper().strip()
        name = input('Optional - Enter a custom name for fund: ')

        if name == '':
            name = None

        if not self._find(symbol):

            fund = self.ft.instantiate_fund(symbol, name)
            self.ft.funds.append(fund)

            if fund in self.ft.funds:
                print(f'{symbol} has been added.')
            else:
                print(f'Unable to add {symbol}.')

            return

        else:
            print(f'Cannot add {symbol}, as it has already been added.')
            return

    def _delete(self):
        """Delete Fund.

        Args:
            None

        Returns:
            None
        """

        log.debug('Deleting fund...')

        symbol = input('Enter the symbol of fund to delete: ')
        symbol = symbol.upper().strip()

        if self._find(symbol):
            self.ft.delete_fund(symbol)
            print(f'Fund {symbol} has been deleted.')
            return

        else:
            print(f'Cannot delete Fund {symbol}, cannot be found.')
            return

    def _show_all(self):
        """Show all Funds.

        Args:
            None

        Returns:
            None
        """

        log.debug('Showing all funds...')

        print(self.ft.generate_all_fund_perf_str())

        return

    def _find(self, symbol):
        """Check for existence of fund.

        Args:
            symbol (str): Symbol for fund.

        Returns:
            Bool: True if fund is located within FundTracker, False otherwise.
        """

        log.debug(f'Checking for existence of fund: {symbol}...')

        for fund in self.ft.funds:
            if fund.symbol == symbol:
                log.debug(f'Fund: {symbol} found.')
                return True

        log.debug(f'Fund: {symbol} not found.')
        return False

    def _invalid(self):
        """Handle invalid inputs.
        Args:
            None

        Returns:
            None
        """

        log.debug('Invalid input.')

        print('Invalid input.')

        return

    def _menu(self):
        """Display menu.

        Args:
            None

        Returns:
            None
        """

        log.debug('Displaying interactive menu.')

        # Display formatting.
        menu_space = 20
        menu_indent = 4

        menu = (
            f"Optional inputs:\n"
            f"{' ' * menu_indent}add{' ' * (menu_space - len('add'))} "
            f"Add a new Fund.\n"
            f"{' ' * menu_indent}delete{' ' * (menu_space - len('delete'))} "
            f"Delete a fund.\n"
            f"{' ' * menu_indent}show all{' ' * (menu_space - len('show all'))} "
            f"Show all Funds.\n"
            f"{' ' * menu_indent}save{' ' * (menu_space - len('save'))} "
            f"Save.\n"
            f"{' ' * menu_indent}quit{' ' * (menu_space - len('quit'))} "
            f"quit.\n"
        )

        print(menu)

        return

    def _save(self):
        """Save program data.

        Args:
            None

        Returns:
            None
        """

        log.debug('Saving...')

        self.ft.save()

        print('Data saved.')

        return

    def _quit(self):
        """Quit interactive mode.

        Returns a signal to end the main event loop.

        Args:
            None

        Returns:
            False
        """

        log.debug('Quiting interactive mode.')

        return False


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

    pass


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
