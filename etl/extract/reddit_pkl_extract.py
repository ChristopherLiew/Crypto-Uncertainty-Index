"""
Extract data from pkl files from API to csv format.
NOT ADDED TO CLI / PIPELINES AS IT IS RUN ON AD HOC BASIS
"""

import os
import toml
import pandas as pd
from tqdm import tqdm
from glob import glob
from pathlib import Path
from typing import Union
from utils.serializer import load_fr_pkl
from utils.logger import log
from utils import timer, check_and_create_dir
from snscrape.modules.reddit import (
    Comment,
    Submission,
)

ROOT = Path()
config = toml.load(ROOT / "config" / "etl_config.toml")
reddit_config = config["reddit"]
data_dir = Path(reddit_config["cryptocurrency"]["save_dir"])
dest_dir = data_dir / "csv"


@timer
def reddit_pkl_extract_csv(
    data_dir: Union[str, Path] = data_dir,
    dest_dir: Union[str, Path] = dest_dir,
) -> None:
    """
    Extracts data from ```.pkl``` files encoded as SNScrape Comment and Submission
    dataclasses and converts it into a Data Frame structure in ```.csv``` form. Note:
    Data will be grouped at the subreddit level (i.e. 1 file per subreddit). Removes
    ```[deleted]``` and ```[removed]``` entries.

    Args:
        data_dir (Union[str, Path]): Folder with pkl files. Expects the following structure:

        data_dir
        |___ subreddit_A
        |    |___ tranche_1.csv
        |    |___ tranche_2.csv
        |___ subreddit_B
        |___ subreddit_C

        Data Directory -> Subreddit Directory -> Pickle Files
        dest_dir (Union[str, Path]): Destination folder to save data in csv format.
    """
    data_dir_path = os.path.join(str(data_dir), "*")
    dirs = glob(data_dir_path, recursive=True)
    print(data_dir_path)
    dirs = [d for d in dirs if not d.endswith("csv")]
    log.info(
        f"""Extracting pkl-ed data from the following subdirections:
             {dirs}"""
    )
    for dir in tqdm(dirs):
        log.info(f"Extracting data from: {dir}")
        cols = ["subreddit", "id", "created", "author", "full_text"]
        dir_name = dir.split("/")[-1]
        dir_data = pd.DataFrame(columns=cols)
        dumps = glob(os.path.join(dir, "*.pkl"))
        for dump in tqdm(dumps, leave=True):
            log.info(f"Extracting subdirectory data from {dump}")
            pkl_data = load_fr_pkl(dump)
            # Process Submission and Comment data
            pkl_data_processed = []
            for data in pkl_data:
                data_dict = data.__dict__
                if isinstance(data, Comment) and data_dict.get("body") not in (
                    "[removed]",
                    "[deleted]",
                ):
                    pkl_data_processed.append(
                        {
                            "subreddit": data_dict["subreddit"],
                            "id": data_dict["id"],
                            "created": data_dict["created"],
                            "author": data_dict["author"],
                            "full_text": str(data_dict["body"]),
                            "type": "comment",
                        }
                    )
                elif isinstance(data, Submission) and data_dict.get("selftext") not in (
                    "[removed]",
                    "[deleted]",
                ):
                    pkl_data_processed.append(
                        {
                            "subreddit": data_dict["subreddit"],
                            "id": data_dict["id"],
                            "created": data_dict["created"],
                            "author": data_dict["author"],
                            "full_text": str(data_dict["title"])
                            + " "
                            + str(data_dict["selftext"]),
                            "type": "submission",
                        }
                    )
                else:
                    # Deleted or not of Correct Class type => Just skip
                    continue
            pkl_data_df = pd.DataFrame(pkl_data_processed, columns=cols)
            dir_data = pd.concat([dir_data, pkl_data_df], axis=0)
        log.info(
            f"Data Extraction for directory: {dir} complete! Writing\
            {len(dir_data)} rows to CSV"
        )
        dest_dir_path = Path(str(dest_dir))
        check_and_create_dir(dest_dir_path)
        dir_data.to_csv(dest_dir_path / f"{dir_name}.csv", index=False)
    log.info("All data extracted!")


# Run
reddit_pkl_extract_csv(data_dir=data_dir, dest_dir=dest_dir)

# Test
eth_df = pd.read_csv(
    "/Users/christopherliew/Desktop/Y4S1/HT/crypto_uncertainty_index/etl/raw_data_dump/reddit/csv/ethereum/ethereum.csv"
)
eth_df.info()
