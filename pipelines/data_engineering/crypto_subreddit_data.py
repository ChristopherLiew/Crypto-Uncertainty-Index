"""
Extract all relevant reddit crypto data and insert to ES.
"""

import os  # Change to PathLib
from typing import List, Optional, Any, Dict
from datetime import datetime
from tqdm import tqdm
from rich.table import Table
from rich.console import Console
from config.reddit_data_cfg import (
    # CRYPTO_REDDIT_DATE_RANGE,
    # CRYPTO_SUBREDDITS,
    REDDIT_DATA_SAVE_DIR,
)
from pathlib import Path
from utils import (
    timer,
    gen_date_chunks,
    check_and_create_dir
)
from utils.logger import log
from utils.serializer import write_to_pkl
from etl.extract.reddit_extract import (
    extract_subreddit_data,
    insert_reddit_to_es
)


@timer
def elt_crypto_subreddit_data(
    subreddits: List[str],
    start_date: datetime,
    end_date: datetime,
    mem_safe: bool = True,
    safe_exit: bool = True,
) -> Optional[Dict[str, Any]]:
    # Accumulators
    log.info("Generating date chunks for batch extraction")
    date_month_batches = gen_date_chunks(start_date=start_date, end_date=end_date)
    crypto_all_data = {}
    # Summary Table
    console = Console()
    summary_table = Table(show_header=True, header_style="bold magenta")
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
        # Kwargs
        for j in tqdm(range(len(date_month_batches)), leave=False):
            batch_start_date, batch_end_date = date_month_batches[j]
            log.info(
                f"""Extracting data for date range:
                {batch_start_date} ~ {batch_end_date}"""
            )
            sub_batch_data = extract_subreddit_data(
                subreddit=sub,
                start_date=batch_start_date,
                end_date=batch_end_date,
                limit=9999999,
                scaper="pmaw",
                mem_safe=mem_safe,
                safe_exit=safe_exit,
            )
            sub_all_data.extend(sub_batch_data)
            # Add stats to summary table
            sub_table_data.append(
                "0" if not sub_batch_data else str(len(sub_batch_data))
            )
            # Serialize data to pkl for safety into
            subreddit_dump_dir = Path(REDDIT_DATA_SAVE_DIR) / sub
            check_and_create_dir(subreddit_dump_dir)
            file_path = (
                subreddit_dump_dir /
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
