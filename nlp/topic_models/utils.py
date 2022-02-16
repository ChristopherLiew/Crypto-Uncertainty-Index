"""
Common Topic Modelling Utils.
"""

import csv
import polars as pl
from typing import Union
from pathlib import Path
from utils.logger import log


def create_big_corpus(data_dir: Union[str, Path],
                      col_name: str,
                      save_file_name: str,
                      save_dir: Union[str, Path]
                      ) -> None:
    """
    Reads all csv files in a given directory and combines
    all rows for a given column into a single csv file.

    Args:
        data_dir (Union[str, Path]): Directory where csv files are located.
        sel_col (str): Column of choice denoted by column name.
    """
    data_dir_path = data_dir if isinstance(data_dir, Path) else Path(data_dir)
    save_dir_path = save_dir if isinstance(save_dir, Path) else Path(save_dir)
    data_files_paths = data_dir_path.rglob("*.csv")
    log.info(f"Reading csv files from: {data_dir} at column {col_name}")
    data = [
        pl.read_csv(v, columns=[col_name])
        for v in data_files_paths
    ]
    log.info(f"Writing csv data to {save_dir}")
    with open(save_dir_path / save_file_name, 'w', newline='') as new_csv_file:
        csv_writer = csv.writer(new_csv_file)
        for df in data:
            csv_writer.writerows(
                df.to_series(0)
                .drop_nulls()
                .to_list()
            )
    log.info(f"Data sucessfully combined and saved to {data_dir}")


# Test
# create_big_corpus(
#     data_dir="nlp/topic_models/data/processed_reddit",
#     col_name="full_text",
#     save_file_name="crypto_processed_reddit_combined.csv",
#     save_dir="nlp/topic_models/data/processed_reddit"
# )
