"""
Utils for data / etl processing
"""

# Process pkl files to csv files save
import toml
from pathlib import Path
from typing import Union
from snscrape.modules.reddit import (
    Comment,
    Submission,
)


ROOT = Path()
config = toml.load(ROOT / "config" / "etl_config.toml")
reddit_config = config["reddit"]
data_dir = Path(reddit_config["save_dir"])
dest_dir = data_dir / "csv"


def reddit_pkl_extract_csv(
    data_dir: Union[str, Path] = data_dir, dest_dir: Union[str, Path] = dest_dir
) -> None:
    """
    Extracts data from ```.pkl``` files encoded as SNScrape Comment and Submission
    dataclasses and converts it into a Data Frame structure in ```.csv``` form. Note:
    Data will be grouped at the subreddit level (i.e. 1 file per subreddit).

    Args:
        data_dir (Union[str, Path]): Folder with pkl files. Expects the following structure:
        Data Directory -> Subreddit Directory -> Pickle Files
        dest_dir (Union[str, Path]): Destination folder to save data in csv format.
    """
    # 1) For each subreddit folder:
    #   2) For each file in folder -> Process:
    #       - Read Comment and Submission objects
    #       - Extract all fields
    #       - Append to dataframe
    #   3) Once completed for that folder write to csv
    # 4) Continue with other folders

    pass
