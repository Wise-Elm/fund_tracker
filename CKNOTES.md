# Notes to help Chris Understand Structure
- Minor changes to format in `README.md` so that the Markdown format
  is interpreted on github and displayed "nicely"
- Dependency requires `pip install yahoofinancials` and `pip install
  yfinance` to set up
- Unsure of the basic usage pattern, some sample runs or usage message
  would help this
- Trying a basic invocation as `python financeapp.py --add RHT` but
  this leads to an exception - is this the correct way to do this?
- `python financeapp.py --add GOOGL` works indicating that it the
  above RHT is probably a non-existent stock symbol but there should
  be handling of attempts to add a missing one.
- `python financeapp.py --getall` correctly iterates and shows info on stocks
- `python financeapp.py --test` seems to correctly run tests
  

# Suggested Changes
## String Formatting
In some spots, the string formatting can be simplified. One example is
in the `generate_fund_performance_str()` function. The original code
had 3 cases for appending a change over the last day, week, and year
in the following style.
```python
# Original Version:
if day:
    day_change = '{:.2f}'.format(self.day_performance(fund)[0])
    if day_change[0] != '-':  # Add '+' when number is not negative.
        day_change = '+' + day_change
    performance += '\n' + f'Previous 24 hours: {day_change}%'
```

This can be simplified and made more regular by using a shared format
string among the 3 cases as in the following.
```python
fmt = "\n{:18}: {:+6.2f}"
if day:
    performance += fmt.format('Previous 24 hours',
                              self.day_performance(fund)[0])
if week:
    performance += fmt.format('Previous year',
                              self.week_performance(fund)[0])

if year:
    performance += fmt.format('Previous year',
                              self.year_performance(fund)[0])
```

## Date / Prices within Fund
It seems like one of the primary things that the Fund class (defined
in `core.py`) accomplishes is to track a correspondence of day to
price in a list of lists. This is set up in the `__init__` function
for Fund and the data comes from an online source like date/time. The
constructor smartly converts this data from the original textural
format to an internal date format:

```
(PDB) p self.dates_prices
[[datetime.date(2020, 4, 14), 59.06999969482422],
 [datetime.date(2020, 4, 15), 57.689998626708984],
 [datetime.date(2020, 4, 16), 57.970001220703125],
 [datetime.date(2020, 4, 17), 59.63999938964844],
 [datetime.date(2020, 4, 20), 58.619998931884766],
 ...
]
```

Later in the code, there are a number of spots where a "closest" date
is needed. See for instance the FundTracker `get_most_current_price()`
function. It uses a linear loop through the `dates_prices` list while
it searches for an appropriate date
```python
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
```
This hand-coded routine can be greatly simplified with Python's
builtin `bisect` module which provides routines to search within
sorted array. The sorted nature of the array can be exploited via
binary search which will make the searches faster ( O(log N) vs the
current O(N) ). A short example appears below demonstrating the
utility of bisect and its routines (better known as binary search).
```python
$> python
Python 3.10.2 (main, Jan 15 2022, 19:56:27) [GCC 11.1.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import bisect         # bisect module for binary search

>>> lst = [1, 5, 7, 9]          # sorted list
>>> bisect.bisect_left(lst, 5)  # search for 5 in list
1                               # found at index 1
>>> bisect.bisect_left(lst, 9)  # search for 9
3                               # found at index 3
>>> bisect.bisect_left(lst, 4)  # search for 4
1                               # not present but insert at index 1 to maintain sorted order
>>> bisect.bisect_left(lst, 10) # search for 10
4                               # not present but insert at index 4 to maintain sorted order
>>> bisect.bisect_left(lst, -3) # etc.
0

>>> lst = [[1,"a"], [5,"b"], [7,"c"], [9,"d"]]    # sorted list of key is the number mirroring dates

>>> bisect.bisect_left(lst, 5, key=(lambda dp: dp[0])) # use a small "key" function to extract to 0th 
1                                                      # element of the nested list for the same
>>> bisect.bisect_left(lst, 9, key=(lambda dp: dp[0])) # effect as the above examples 
3
>>> bisect.bisect_left(lst, 2, key=(lambda dp: dp[0]))
1
```
Ultimately the hand-written linear search can be re-written as a call to bisect:
```
        # alternative to the linear search above using bisect module
        bindex = bisect.bisect_left(fund.dates_prices, date_, key=(lambda dp: dp[0]))
```



To further improve speed, it may be worthwhile to reformat the dates
and prices in parallel lists as in:

```
dates=[datetime.date(2020, 4, 14), datetime.date(2020, 4, 15), datetime.date(2020, 4, 16), datetime.date(2020, 4, 17), datetime.date(2020, 4, 20), ...]
price=[59.0699996948242,           57.6899986267089,           57.9700012207031,           59.6399993896484,           58.6199989318847, ...]
```

but this will require some re-arrangement of the internal data to get
things right and may be more trouble than it is worth.

I'd strongly suggest that several of the access functions be moved
from FundTracker to Fund itself, particularly the `get_price()` type
functions. Prices and the dates associated with them that are
available for a given fund are an internal property of that
class. Ideally one would write something like:

```python
  (price, actual_date) = fund.get_price_at_date(date)
```

which would use the internal information within the fund to search the
list of dates, find the closest date to that requested, and return the
associated price and perhaps an actual date for the price if the one
requested was not present exactly.  This has several good effects
1. It allows the Fund class to re-arrange how dates and prices are
   internally stored, in a list of lists or parallel lists, or another
   data structure. 
2. Requests for prices/dates dispatch to methods of the Fund
   class itself which can employ the most efficient search mechanism
   available such as binary search.
3. It makes the remaining code much shorter and easier to
   understand. For instance, functions like `day_performance()` can be
   simplified in something like the following:
   
OLD VERSION
```python
def day_performance(self, fund):
    
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

```
   
PROPOSED VERSION
```python
def day_performance(self, fund):
    
        (b_price, b_date) = fund.get_price(NOW)
        (a_price, a_date) = fund.get_price(NOW - timedelta(days=1)
        difference = self.calculate_percentage(a_price, b_price)

```
   
## Fund vs FundTracker
Many of the FundTracker methods may be better placed in the Fund
itself though this is a matter of taste. I tend to think of the
performance of a Fund as "belonging" to the fund, a property of it
that deserves to be a method of Fund, but others may differ a bit on
this. If you follow my mental model, functions like the following
probably belong in Fund rather than FundTracker

```
def generate_fund_performance_str(self, fund, day=True, week=True, year=True):
def custom_range_performance(self, fund, start_date, end_date):
def day_performance(self, fund):
def week_performance(self, fund):
def year_performance(self, fund):
def get_most_current_price(self, fund, search_date=None):
def calculate_percentage(self, first_price, last_price):
```

All of them are suspect as they take fund arguments and don't seem to
interact with the fields and methods of FundTracker, rather working
on/with data in Funds.  This is usually a sign that they below with
the Fund class.

## calculate_percentage() function
This function doesn't need to be in any class and can be moved outside
any class, likely where it belongs as it has no dependencies on
anything except its arguments. I've done this and also provided a
slightly more concise version of the calculation.

## Single Module for Yahoo Financial Interface
There appear to be two source files to support drawing data from
Yahoo:
- `pull_from_yf.py` which performs the actual API call
- `controller_for_yf.py` which reformats the data retrieved into the
  format used by the remainder of the application
I can see some reasons to separate these two but in the interest of
conciseness, it may be worthwhile to merge them. 

This suggestion is based only a loose understanding of the goals but I
don't think that there needs to be too much distinction between these
two parts: any data source will have a download + reformat flavor to it.

One way to check whether this would be a good idea or not would be to
explore how easy or difficult adding a second data source might be. It
looks like Google has a related API to query similar information here

https://pypi.org/project/googlefinance/

Often times it takes analysis of 2-3 different instances of a source
like this before the common pattern takes shape and one can develop a
framework that is really extensible.
