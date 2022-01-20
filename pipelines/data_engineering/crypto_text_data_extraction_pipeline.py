"""
Extract all relevant reddit crypto data and insert to ES.
"""

from typing import (
    List,
    Optional,
    Any,
    Dict
)
from datetime import datetime
from tqdm import tqdm
from rich.table import Table
from rich.console import Console
from config.reddit_data_cfg import (
    CRYPTO_REDDIT_DATE_RANGE,
    CRYPTO_SUBREDDITS
)
from utils import (
    timer,
    gen_date_chunks
)
from utils.logger import log
from data.extract.reddit_extract import (
    get_all_crypto_subreddit_data,
    insert_reddit_to_es
)
from data.schema.pmaw_reddit_objects import (
    SubmissionPMAW,
    CommentPMAW
)


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
                batch_end_date,
                max_results_per_subreddit=None
            )
            sub_all_data.extend(sub_batch_data)
            sub_table_data.append(
                0 if not sub_batch_data else len(sub_batch_data)
            )
        log.info(f"Extraction for subreddit: {sub} complete!")
        crypto_all_data[sub] = sub_all_data
        summary_table.add_row(*sub_table_data)  # Append subreddit res to table
    console.print(summary_table)
    return crypto_all_data
    # log.info("Inserting data into Elasticsearch")
    # insert_reddit_to_es(crypto_all_data)
    # log.info("Insertion to Elasticsearch complete")
    # # Print out summary table
    # console.print(summary_table)


# Test
test_subreddit = [CRYPTO_SUBREDDITS[0]]  # ethereum
# 1 year of data
start_date, end_date = (
    datetime(2021, 12, 30),
    datetime(2021, 12, 31)
)
# Run pipeline
eth_sr_one_year_data = elt_crypto_reddit_data(
    subreddits=test_subreddit,
    start_date=start_date,
    end_date=end_date
)
