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
  

