# Title

         __                __     _____  __    __    __        __   __  
        |__   |  |  |\ |  |  \      |   |__\  |__|  |    |_/  |_   |__\ 
        |     |__|  | \|  |__/      |   |  \  |  |  |__  | \  |__  |  \ 


By Graham Steeds

# Context

An application derived to provide easily accessible and readable financial fund data
to the user through the use of a interactive shell interface mode, and a more robust 
direct shell command prompt structure. Fund Tracker is ideas for use as a cron job, or 
as a simple and quick way to check a custom selection of money market account data.



This module incorporates foreign modules to retrieve data, and handles simultaneous 
data collection through the use of Multithreading while managing dependencies, 
abstraction leaks, and errors.

# Description

Fund Tracker (FT) provides the user with an easy tool for tracking the history of money 
market accounts such as Mutual Funds and Stocks.

The user may provide a list of money market accounts in which to track and FT will 
provide the user with the ability so save those accounts to disc for future ease of use 
recovery. Provided to the user is a standard set of history data for each account 
including the display of fund performance over the previous 24 hour, previous week, 
and previous year. Additionally, users can specify a date range and view the 
performance of any fund over any period of time. Since fund symbols can be obscure, FT 
provides the ability to assign a custom name to each fund to make data easier to read.

# Design

FT is designed from the ground up to be easily accessible and expandable by other 
programmers.

In keeping with these concepts:

- FT is designed for the easy addition of external modules as desired.
- Robust logging and error handling are built in.
- Unit testing is incorporated.
- Repo is set up to easily incorporate attentional file type handling.
- FT outputs are easily customizable.
- FT is fully documented and commented.

Since the majority of runtime is spent waiting on IO bound network connections 
a custom multithreading module is included to control timeouts, network issues, and 
provide the ability to make network request synchronously.


# Using Fund Tracker

Fund Tracker may be used by running fund_tracker.sh which will launch the program in 
interactive mode. Interactive mode provides the core functionality of the program 
while limiting more obscure use cases, and provides a user friend platform.

    $ ./fund_tracker.sh

Fund Tracker can also be run directly from the shell.
Activate the virtual environment:

    $ source venv/bin/activate

The use Python to run the program. This example brings up the help text:
    
    $ python fund_tracker.py -h


# Application examples

## Menu


    Welcome to:
         __                __     _____  __    __    __        __   __  
        |__   |  |  |\ |  |  \      |   |__\  |__|  |    |_/  |_   |__\ 
        |     |__|  | \|  |__/      |   |  \  |  |  |__  | \  |__  |  \ 

    
    Application is being run in persistent mode. Enter 'menu' for a list of options, or 
    'quit' to exit.
    
    Enter your selection: menu
    Optional inputs:
        add                  Add a new Fund.
        delete               Delete a fund.
        show all             Show all Funds.
        save                 Save.
        quit                 quit.
    
    
    Enter your selection: 



## Example Output for funds FBGRX.

The standard output presents the fund symbol followed by frequently desired fund 
information such as the latest price, and performance over the previous 24, week, and 
year of trading. Following is a graph showing the pricing over the previous year.

    FBGRX - 
    USD - MUTUALFUND
    Latest price: 2022-05-06 - $133.53
    Previous 24 hours :  +1.58
    Previous week     :  -2.99
    Previous year     : -23.25
    
                                          ******                                                        |$198.19
                               *   ****  *                                                              |
                      ******  * ***    **             *     *                                           |
                   ***      **                   *  **   ***                                            |
              * ***                             * **   **                                               |
    *     **** *                                             ***                                        |
     * * *                                                      *                                       |
      * *                                                        *    *  *                              |
                                                                  *     *  *           ******           |
                                                                   * * *  * *  **     *      *          |
                                                                    *        **      *         * *      |
                                                                                 * *          * *       |
                                                                                  *               * * * |
                                                                                    *              * *  |
                                                                                                       *|$133.53
    ____________________________________________________________________________________________________|
    2021-05-07                                                                                2022-05-06
    ****************************************************************************************************
    

# Python

Fund Tracker was developed and tested with python 3.10.4.

## Dependencies

The virtual environment will require the following dependencies:

- beautifulsoup4==4.10.0
- certifi==2021.10.8
- charset-normalizer==2.0.12
- idna==3.3
- python-dateutil==2.8.2
- pytz==2021.3
- six==1.16.0
- soupsieve==2.3.1
- urllib3==1.26.8
- yahoofinancials==1.6

Version accurate as of 05-05-2022.
