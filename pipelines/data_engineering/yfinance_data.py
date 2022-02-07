"""
Pipeline to extract and ingest Cryptocurrency Price data.

See: https://github.com/ranaroussi/yfinance
"""

import toml
from typing import Union, List
from pathlib import Path
import yfinance as yf
from utils.logger import log
from postgres.utils import pd_to_pg
from sqlalchemy import create_engine


# Config
pg_config = toml.load(Path() / "config" / "etl_config.toml")["postgres"]
pg_engine = create_engine(pg_config["default_local_uri"], echo=True)


yfin_to_pg_map = {
    "ticker": "ticker",
    "Date": "date",
    "Open": "open",
    "Close": "close",
    "High": "high",
    "Low": "low",
    "Adj Close": "adj_close",
    "Volume": "volume",
}


# Pipeline
def elt_yfinance_data(
    tickers: Union[str, List[str]],
    start_date: str,
    end_date: str,
    interval: str = "1wk",
    threads: bool = True,
    dest_table: str = pg_config["tables"]["asset_price_table"],
) -> None:

    ticker_list = tickers
    if isinstance(tickers, List):
        tickers = " ".join(tickers)

    log.info("Pulling data from Yahoo Finance")

    data = yf.download(
        tickers=tickers,
        start=start_date,
        end=end_date,
        interval=interval,
        threads=threads,
        group_by="ticker",
    )

    if len(ticker_list) > 1:
        for tick in ticker_list:
            log.info(f"Inserting {tick} data to {dest_table}")
            ticker_data = (
                data[tick].dropna().reset_index().rename(columns=yfin_to_pg_map)
            )
            ticker_data["ticker"] = tick
            (ticker_data.to_sql(dest_table, pg_engine, index=False, if_exists="append"))

    log.info("All data sucessfully inserted!")
