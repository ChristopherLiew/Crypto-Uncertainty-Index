"""
CLI commands for easy pipeline triggers and model training,
inference and analysis, etc.
"""

import ast
import typer
import toml
from nlp.cli import nlp_app
from pathlib import Path
from typing import List
from datetime import datetime
from es.manager import ESManager
from etl.schema.es_mappings import (
    REDDIT_CRYPTO_INDEX_NAME,
    REDDIT_CRYPTO_CUSTOM_INDEX_NAME,
    reddit_crypto_custom_mapping,
)
from pipelines.data_engineering.yfinance_data import elt_yfinance_data
from pipelines.data_engineering.crypto_subreddit_data import elt_crypto_subreddit_data
from pipelines.crypto_index.ucry_indices import construct_ucry_index
from etl.load.ucry_load import insert_ucry_to_es
from postgres.utils import pd_to_pg

# App
app = typer.Typer()

# Details
__app_name__, __version__ = "ucry-cli", "0.1.0"

# Config
DATE_FMT = "%Y-%m-%d"
ROOT = Path()
config = toml.load(ROOT / "config" / "etl_config.toml")
reddit_config = config["reddit"]
crypto_config = reddit_config["cryptocurrency"]
pg_config = config["postgres"]
yf_config = config["yfinance"]


# Add additional Apps
app.add_typer(nlp_app, name="nlp-toolkit", help="NLP modelling and processes toolkit")


#####################
## Data Extraction ##
#####################
CRYPTO_SUBREDDITS = crypto_config["crypto_subreddits"]
START_DATE, END_DATE = (
    datetime.strptime(crypto_config["start_date"], DATE_FMT),
    datetime.strptime(crypto_config["end_date"], DATE_FMT),
)

# Run Extraction
@app.command(
    "extract-reddit-cry-data",
    help="Extracts data from given subreddits for the specified date range.",
)
def run_elt_crypto_subreddit_pipe(
    subreddits: List[str] = typer.Option(
        CRYPTO_SUBREDDITS, help="Subreddits to pull data from"
    ),
    start_date: datetime = typer.Option(START_DATE, help="Start date"),
    end_date: datetime = typer.Option(END_DATE, help="End date"),
    mem_safe: bool = typer.Option(
        True, help="Toggle memory safety. If True, caches extracted data periodically"
    ),
    safe_exit: bool = typer.Option(
        False,
        help="Toggle safe exiting. If True, extraction will pick up where it left off if interrupted",
    ),
) -> None:
    f"""
    Extracts data from selected subreddits for a given date range and inserts
    results into Elasticsearch index ```{REDDIT_CRYPTO_INDEX_NAME}```. Also
    pickles data into ```data/raw_data_dump/reddit```.

    Args:
        start_date (str, optional): Start Date (Format = %Y-%m-%d). Defaults to 2014-01-01
        end_date (str, optional): End date (Format = %Y-%m-%d). Defaults to 2021-12-31
    """

    return elt_crypto_subreddit_data(
        subreddits=subreddits,
        start_date=start_date,
        end_date=end_date,
        mem_safe=mem_safe,
        safe_exit=safe_exit,
    )


# Get yfinance data
@app.command("extract-yfin-data", help="Extracts ticker data from Yahoo Finance")
def run_elt_yfinance_pipe(
    tickers: List[str] = typer.Option(
        yf_config["tickers"], help="List of Asset Tickers"
    ),
    start_date: str = typer.Option(
        yf_config["start_date"], help="Start date to begin extraction"
    ),
    end_date: str = typer.Option(
        yf_config["end_date"], help="End date to extract up till"
    ),
    interval: str = typer.Option(yf_config["frequency"], help="Granularity of data"),
    target_table: str = typer.Option(
        pg_config["tables"]["asset_price_table"],
        help="Postgres table to insert data to",
    ),
) -> None:
    elt_yfinance_data(
        tickers=tickers,
        start_date=start_date,
        end_date=end_date,
        interval=interval,
        dest_table=target_table,
    )


############################
## Data & Text Processing ##
############################

# ES Reindex
# -> Change dest mapping to allow JSON files as well
@app.command(
    "es-reindex", help="ES reindexing from a source index to a destination index"
)
def run_es_reindex(
    source_index: str = typer.Option(
        REDDIT_CRYPTO_INDEX_NAME, help="Source ES Index to pull data from"
    ),
    dest_index: str = typer.Option(
        REDDIT_CRYPTO_CUSTOM_INDEX_NAME, help="Destination ES Index to insert data to"
    ),
    dest_mapping: str = typer.Option(
        reddit_crypto_custom_mapping,
        help="Destination index ES mapping",
        show_default=False,
    ),
) -> None:

    es_conn = ESManager()

    if not es_conn.index_is_exist(dest_index):
        es_conn.create_index(
            index=dest_index,
            mapping=ast.literal_eval(dest_mapping),
            separate_settings=False,
        )

    es_conn.reindex(source_index=source_index, dest_index=dest_index)


#################################
## Uncertainty Index Pipelines ##
#################################
def complete_lucey_ucry_type():
    return ["price", "policy"]


@app.command(
    name="build-ucry-index",
    help="Construct crypto uncertainty index based on Lucey's methodology.",
)
def construct_lucey_index(
    es_source_index: str = typer.Option(
        REDDIT_CRYPTO_CUSTOM_INDEX_NAME, help="ES Index to pull text data from"
    ),
    start_date: datetime = typer.Option(START_DATE, help="Start date"),
    end_date: datetime = typer.Option(END_DATE, help="End date"),
    granularity: str = typer.Option(
        "week", help="Supports day, week, month, year etc."
    ),
    text_field: str = typer.Option("full_text", help="Name of field to mine for index"),
    type: str = typer.Option(
        "price",
        help="Index type. One of price or policy",
        autocompletion=complete_lucey_ucry_type,
    ),
    prefix: str = typer.Option(
        "lucey", help="Index name. One of lucey, lda or top2vec"
    ),
) -> None:

    index_df = construct_ucry_index(
        es_source_index=es_source_index,
        start_date=start_date,
        end_date=end_date,
        granularity=granularity,
        type=type,
        text_field=text_field,
        prefix=prefix,
    )

    # Insert to ES index
    insert_ucry_to_es(index_df)
    # Insert to PG table
    pd_to_pg(index_df, table_name="ucry_index")


if __name__ == "__main__":
    app()
