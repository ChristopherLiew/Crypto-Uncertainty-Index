"""
Common Topic Modelling Utils.
"""

import csv
from tqdm import tqdm
import polars as pl
from typing import Union
from pathlib import Path
from utils.logger import log


def create_big_corpus(data_dir: Union[str, Path],
                      sample_pct: float,
                      col_name: str,
                      save_file_name: str,
                      save_dir: Union[str, Path]
                      ) -> None:
    """
    Constructs a single csv file from multiple csvs based on a single
    column's data.

    Args:
        data_dir (Union[str, Path]): Source directory containing csv files
        sample_pct (float): Sampling fraction
        col_name (str): Name of column to extract data from
        save_file_name (str): Name of file to save it as
        save_dir (Union[str, Path]): Directory to save it at
    """
    data_dir_path = data_dir if isinstance(data_dir, Path) else Path(data_dir)
    save_dir_path = save_dir if isinstance(save_dir, Path) else Path(save_dir)
    data_files_paths = data_dir_path.rglob("*.csv")
    log.info(f"Reading csv files from: {data_dir} at column {col_name}")
    data = [
        pl.read_csv(v, columns=[col_name])
        .sample(frac=sample_pct)
        for v in data_files_paths
    ]
    log.info(f"Writing csv data to {save_dir}")
    with open(save_dir_path / save_file_name, 'w', newline='', encoding='UTF8') as new_csv_file:
        csv_writer = csv.writer(new_csv_file)
        # Header
        csv_writer.writerow([col_name])
        # Body
        [
            csv_writer.writerow([r]) for df in tqdm(data)
            for r in tqdm(df.to_series(0).drop_nulls().to_list(), leave=True)
        ]
    log.info(f"Data sucessfully combined and saved to {data_dir}")


# Test
# create_big_corpus(
#     data_dir="nlp/topic_models/data/processed_reddit",
#     sample_pct=0.50,  # Stratified by CSV file
#     col_name="full_text",
#     save_file_name="crypto_processed_reddit_combined_50.csv",
#     save_dir="nlp/topic_models/data/processed_reddit_combined"
# )

# x = pl.read_csv('nlp/topic_models/data/processed_reddit_combined/crypto_processed_reddit_combined_50.csv')
# len(x)
