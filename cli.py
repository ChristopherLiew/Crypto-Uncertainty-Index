"""
CLI commands for easy pipeline triggers and model training,
inference and analysis, etc.
"""

import typer
from typing import (
    Optional,
    List
)
from datetime import datetime
from pipelines.data_engineering.crypto_subreddit_data import (
    elt_crypto_subreddit_data
)
from config.reddit_data_cfg import (
    CRYPTO_REDDIT_DATE_RANGE
)
from data.schema.es_mappings import (
    REDDIT_CRYPTO_INDEX_NAME
)

# App
app = typer.Typer()

# Details
__app_name__, __version__ = "crypto-uncertainty-index", "0.1.0"


# Callback
def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Applcations version",
        callback=_version_callback,
        is_eager=True
    )
) -> None:
    return


@app.command("hello-world")
def hello_world(name: str) -> None:
    print(f"Hello there {name}, welcome to the cli interface")


#####################
## Data Extraction ##
#####################
START_DATE, END_DATE = CRYPTO_REDDIT_DATE_RANGE.values()


# Run Extraction
@app.command("extract-reddit-cry-data",
             help="Extracts data from given subreddits for the specified date range.")
def run_elt_crypto_subreddit_pipe(subreddits: List[str],
                                  start_date: datetime = typer.Option(START_DATE),
                                  end_date: datetime = typer.Option(END_DATE),
                                  mem_safe: bool = typer.Option(True),
                                  safe_exit: bool = typer.Option(False)
                                  ) -> None:
    f"""
    Extracts data from selected subreddits for a given date range and inserts
    results into Elasticsearch index ```{REDDIT_CRYPTO_INDEX_NAME}```. Also
    pickles data into ```data/raw_data_dump/reddit```.

    Args:
        start_date (str, optional): Start Date (Format = %Y-%m-%d). Defaults to 2014-01-01
        end_date (str, optional): End date (Format = %Y-%m-%d). Defaults to 2021-12-31
    """
    return (
        elt_crypto_subreddit_data(subreddits=subreddits,
                                  start_date=start_date,
                                  end_date=end_date,
                                  mem_safe=mem_safe,
                                  safe_exit=safe_exit)
    )


#####################
## Data Processing ##
#####################


###################
## NLP Pipelines ##
###################


# Entry point
if __name__ == "__main__":
    app()
