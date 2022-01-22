"""
Extract all relevant reddit crypto data and insert to ES.
"""

import os  # Change to PathLib
from pprint import pprint
from typing import (
    List,
    Optional,
    Any,
    Dict
)
from typer import Typer
from datetime import datetime
from tqdm import tqdm
from rich.table import Table
from rich.console import Console
from config.reddit_data_cfg import (
    # CRYPTO_REDDIT_DATE_RANGE,
    # CRYPTO_SUBREDDITS,
    REDDIT_DATA_SAVE_DIR
)
# from es.manager import ESManager
from utils import (
    timer,
    gen_date_chunks
)
from utils.logger import log
from utils.serializer import (
    write_to_pkl
)
from data.extract.reddit_extract import (
    get_all_crypto_subreddit_data,
    insert_reddit_to_es
)
# from data.schema.es_mappings import REDDIT_CRYPTO_INDEX_NAME


# Instantiate nested Typer App
app = Typer()


@timer
def elt_crypto_reddit_data(subreddits: List[str],
                           start_date: datetime,
                           end_date: datetime) -> Optional[Dict[str, Any]]:
    # Accumulators
    log.info("Generating date chunks for batch extraction")
    date_month_batches = gen_date_chunks(start_date=start_date,
                                         end_date=end_date)
    crypto_all_data = {}
    # Summary Table
    console = Console()
    summary_table = Table(
        show_header=True,
        header_style="bold magenta"
    )
    summary_table.add_column("Subreddit")
    for s, e in date_month_batches:
        summary_table.add_column(f"{s.date()} ~ {e.date()}")
    # Extraction
    for i in tqdm(range(len(subreddits))):
        sub = subreddits[i]
        log.info(f"Extracting data from subreddit: {sub}")
        # For each batch of months
        sub_all_data = []
        sub_table_data = [sub]
        for j in tqdm(range(len(date_month_batches)), leave=False):
            batch_start_date, batch_end_date = date_month_batches[j]
            log.info(
                f"""Extracting data for date range:
                {batch_start_date} ~ {batch_end_date}"""
                )
            sub_batch_data = get_all_crypto_subreddit_data(
                sub,
                batch_start_date,
                batch_end_date
            )
            sub_all_data.extend(sub_batch_data)
            # Add stats to summary table
            sub_table_data.append(
                '0' if not sub_batch_data else str(len(sub_batch_data))
            )
            # Serialize data to pkl for safety into
            file_path = os.path.join(
                REDDIT_DATA_SAVE_DIR,
                sub,
                f"{sub}_{batch_start_date.date()}_{batch_end_date.date()}.pkl"
            )
            write_to_pkl(file_path=file_path, obj=sub_batch_data)
            # Insert to elasticsearch
            insert_reddit_to_es(data=sub_batch_data)
        log.info(f"Extraction for subreddit: {sub} complete!")
        crypto_all_data[sub] = sub_all_data
        summary_table.add_row(*sub_table_data)  # Append subreddit res to table
    # Print out summary table
    console.print(summary_table)
    return crypto_all_data


# Run Extraction
@app.command()
def run_crypto_extract_pipeline(*subreddits,
                                start_date: datetime,
                                end_date: datetime) -> None:
    subreddits_list = list(subreddits)
    return (
        elt_crypto_reddit_data(subreddits=subreddits_list,
                               start_date=start_date,
                               end_date=end_date)
    )


# # Test
# test_subreddit = [CRYPTO_SUBREDDITS[0]]  # ethereum
# # 1 month of data
# start_date, end_date = (
#     datetime(2014, 1, 1),
#     datetime(2014, 12, 31)
# )
# # Run pipeline
# eth_sr_one_year_data = elt_crypto_reddit_data(
#     subreddits=test_subreddit,
#     start_date=start_date,
#     end_date=end_date
# )
# # Elastic search test
# es_conn = ESManager()
# test_query = {
#     "query": {
#         "bool": {
#             "filter": [
#                 {"term": {"subreddit": f"{CRYPTO_SUBREDDITS[0]}"}}
#             ]
#         }
#     }
# }
# res = (
#     es_conn
#     .run_match_query(index=REDDIT_CRYPTO_INDEX_NAME, query=test_query)
# )

# # Load 2014 cache
# from pmaw import Response
# cache_key = '0defbb20eaa0c9c3eed13a5a10a38cd8'
# cache_dir = './cache'
# resp_2014 = Response.load_cache(cache_key, cache_dir)
# sample_2014 = next(resp_2014)
# pprint(sample_2014)

# # 2020 cache
# cache_key = '5a5c0f0604c9e177440acb9433889380'
# resp_2020 = Response.load_cache(cache_key, cache_dir)
# sample_2020 = next(resp_2020)
# pprint(sample_2020)
