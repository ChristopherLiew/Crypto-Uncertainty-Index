"""
Combine all raw / processed reddit data into a single large csv.
"""

import pandas as pd
from tqdm import tqdm
from pathlib import Path


data_dir_path = Path("nlp/topic_models/data/processed_reddit")
save_data_dir_path = Path("nlp/hedge_classifier/data/reddit_inference")

data_fps = data_dir_path.rglob("*.csv")

data = pd.concat(
    [pd.read_csv(fp, usecols=["created", "full_text"]) for fp in tqdm(data_fps)],
    axis=0,
).reset_index(drop=True)

data["created"] = pd.to_datetime(data["created"])
data.info()

data.to_csv(save_data_dir_path / "full_reddit_inf_corpus.csv")
