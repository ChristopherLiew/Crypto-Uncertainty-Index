"""
CLI commands for easy pipeline triggers and model training,
inference and analysis, etc.
"""

import ast
import typer
from typing import List
from datetime import datetime
from es.manager import ESManager
from etl.schema.es_mappings import (
    REDDIT_CRYPTO_INDEX_NAME,
    REDDIT_CRYPTO_CUSTOM_INDEX_NAME,
    reddit_crypto_custom_mapping
)
from pipelines.data_engineering.crypto_subreddit_data import elt_crypto_subreddit_data
from pipelines.crypto_index.lucey_keyword_based.ucry_indices import (
    insert_ucry_to_es,
    construct_ucry_index
)
from config.reddit_data_cfg import CRYPTO_REDDIT_DATE_RANGE

# App
app = typer.Typer()

# Details
__app_name__, __version__ = "crypto-uncertainty-index", "0.1.0"


@app.command("hello-world")
def hello_world(name: str) -> None:
    print(f"Hello there {name}, welcome to the cli interface")


#####################
## Data Extraction ##
#####################
START_DATE, END_DATE = CRYPTO_REDDIT_DATE_RANGE.values()


# Run Extraction
@app.command(
    "extract-reddit-cry-data",
    help="Extracts data from given subreddits for the specified date range.",
)
def run_elt_crypto_subreddit_pipe(
    subreddits: List[str],
    start_date: datetime = typer.Option(START_DATE),
    end_date: datetime = typer.Option(END_DATE),
    mem_safe: bool = typer.Option(True),
    safe_exit: bool = typer.Option(False),
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


############################
## Data & Text Processing ##
############################

# ES Reindex
# -> Change dest mapping to allow JSON files as well
@app.command('es-reindex',
             help="ES reindexing from a source index to a destination index")
def run_es_reindex(source_index: str = typer.Option(REDDIT_CRYPTO_INDEX_NAME),
                   dest_index: str = typer.Option(REDDIT_CRYPTO_CUSTOM_INDEX_NAME),
                   dest_mapping: str = typer.Option(reddit_crypto_custom_mapping)
                   ) -> None:

    es_conn = ESManager()
    print(es_conn.index_is_exist(dest_index))
    if not es_conn.index_is_exist(dest_index):
        es_conn.create_index(
            index=dest_index,
            mapping=ast.literal_eval(dest_mapping),
            separate_settings=False)

    es_conn.reindex(
        source_index=source_index,
        dest_index=dest_index)


###################
## NLP Pipelines ##
###################


#################################
## Uncertainty Index Pipelines ##
#################################
@app.command(name="build-ucry-lucey",
             help="Construct crypto uncertainty index based on Lucey's methodology.")
def construct_lucey_index(es_source_index: str = typer.Option(REDDIT_CRYPTO_CUSTOM_INDEX_NAME),
                          start_date: datetime = typer.Option(START_DATE),
                          end_date: datetime = typer.Option(END_DATE),
                          granularity: str = typer.Option('week', help="Supports day, week, month, year etc."),
                          text_field: str = typer.Option('full_text', help='Name of field to mine for index'),
                          type: str = typer.Option('price', help="Lucey index type. One of 'price' or 'policy'")) -> None:
    index_df = construct_ucry_index(es_source_index=es_source_index,
                                    start_date=start_date,
                                    end_date=end_date,
                                    granularity=granularity,
                                    type=type,
                                    text_field=text_field)
    insert_ucry_to_es(index_df)


if __name__ == "__main__":
    app()
