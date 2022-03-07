"""
Splits our original corpus of csvs into train and test for each subreddit
for downstream topic modelling.
"""

from typing import Union, Dict
from pathlib import Path
from tqdm import tqdm
import pandas as pd
from sklearn.model_selection import train_test_split
from utils.logger import log


# Config
DEFAULT_DATA_DIR = Path('nlp/topic_models/data/processed_reddit')

DEFAULT_TRAIN_TEST_DIR_MAP = {
    'train': Path('nlp/topic_models/data/processed_reddit_train_test/train'),
    'test': Path('nlp/topic_models/data/processed_reddit_train_test/test'),
}


def train_test_split_reddit(data_dir: Union[str, Path] = DEFAULT_DATA_DIR,
                            test_split: float = 0.1,
                            output_dir_map: Dict[str, str] = DEFAULT_TRAIN_TEST_DIR_MAP
                            ) -> None:
    # Get file paths
    data_dir_path = Path(data_dir)
    data_fps = list(data_dir_path.rglob("*.csv"))
    train_path = Path(output_dir_map['train'])
    test_path = Path(output_dir_map['test'])
    # Load and split data
    for fp in tqdm(data_fps):
        log.info(
            f"Pulling and splitting data from: {fp.name}"
        )
        raw_data = pd.read_csv(fp)
        train_data, test_data = train_test_split(
            raw_data,
            test_size=test_split,
            random_state=42
        )
        file_name = fp.stem
        train_fp = train_path / f"{file_name}_train.csv"
        test_fp = test_path / f"{file_name}_test.csv"
        pd.DataFrame(train_data).to_csv(train_fp)
        pd.DataFrame(test_data).to_csv(test_fp)
        log.info(
            f"""Data from {fp.stem} sucessfully written to:
            - Train: {train_fp}
            - Test: {test_fp}
            """
        )


# Test
train_test_split_reddit(
    data_dir=DEFAULT_DATA_DIR,
    test_split=0.2,
    output_dir_map=DEFAULT_TRAIN_TEST_DIR_MAP
)
