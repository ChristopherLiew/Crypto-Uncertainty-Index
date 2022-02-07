"""
Pipeline to extract and ingest Cryptocurrency Price data.

See: https://github.com/ranaroussi/yfinance
"""

import pandas as pd
from datetime import datetime
from pathlib import Path
import yfinance as yf
from pandas_datareader import data as pdr
from utils.logger import log
from sql.utils import pd_to_pg
from utils import check_and_create_dir

# Pipeline
# Pull data using configs
# Format
# Dump to raw-data-dump
# Insert to PG


def elt_yfinance_data() -> None:
    
yf.pdr_override() # <== that's all it takes :-)

# download dataframe
data = pdr.get_data_yahoo("SPY", start="2017-01-01", end="2017-04-30")

import yfinance as yf
data = yf.download("SPY AAPL", start="2017-01-01", end="2017-04-30")

data = yf.download(  # or pdr.get_data_yahoo(...
    # tickers list or string as well
    tickers = "SPY AAPL MSFT",

    # use "period" instead of start/end
    # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
    # (optional, default is '1mo')
    period = "ytd",

    # fetch data by interval (including intraday if period < 60 days)
    # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
    # (optional, default is '1d')
    interval = "1m",

    # group by ticker (to access via data['SPY'])
    # (optional, default is 'column')
    group_by = 'ticker',

    # adjust all OHLC automatically
    # (optional, default is False)
    auto_adjust = True,

    # download pre/post regular market hours data
    # (optional, default is False)
    prepost = True,

    # use threads for mass downloading? (True/False/Integer)
    # (optional, default is True)
    threads = True,

    # proxy URL scheme use use when downloading?
    # (optional, default is None)
    proxy = None
)
