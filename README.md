# Title

             __   *           _           __   __        _     __   __
            |__   |   |\ |   /_\   |\ |  /    |__       /_\   |_/  |_/
            |     |   | \|  /   \  | \|  \__  |__      /   \  |    |  



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


# Application examples

## Menu


    Welcome to:
             __   *           _           __   __        _     __   __
            |__   |   |\ |   /_\   |\ |  /    |__       /_\   |_/  |_/
            |     |   | \|  /   \  | \|  \__  |__      /   \  |    |  
    
    Application is being run in persistent mode. Enter 'menu' for a list of options, or 'quit' to exit.
    
    Enter your selection: menu
    Optional inputs:
        add                  Add a new Fund.
        delete               Delete a fund.
        show all             Show all Funds.
        save                 Save.
        quit                 quit.
    
    
    Enter your selection: 



## Example Output for funds FBGRX, FNBGX, & FPADX.


    FBGRX - 
    USD - MUTUALFUND
    Latest price: 2022-05-03 - $140.03
    Previous 24 hours :  +0.07
    Previous week     :  +0.96
    Previous year     : -19.27
    ****************************************
    FNBGX - 
    USD - MUTUALFUND
    Latest price: 2022-05-03 - $11.86
    Previous 24 hours :  -0.59
    Previous week     :  -3.26
    Previous year     : -15.77
    ****************************************
    FPADX - 
    USD - MUTUALFUND
    Latest price: 2022-05-03 - $10.60
    Previous 24 hours :  -0.47
    Previous week     :  +3.30
    Previous year     : -19.51
    ****************************************


# TODO

Develop further unittesting.
