"""
Elasticsearch X Torch Dataset for Inference.
"""

from tqdm import tqdm
import pandas as pd
from torch.utils.data import Dataset
from typing import Union, Optional
from pathlib import Path


# Change underlying to Polars for efficiency
class RedditInferenceDataset(Dataset):
    def __init__(
        self,
        data_dir: Union[str, Path],
        text_col: str = "full_text",
        nrows: Optional[float] = None,
    ) -> None:
        self.data_dir_path = Path(data_dir)
        data_fps = self.data_dir_path.rglob("*.csv")
        self.data = pd.concat(
            [pd.read_csv(fp, nrows=nrows, usecols=[text_col]) for fp in tqdm(data_fps)],
            axis=0,
        ).reset_index(drop=True)
        self.text_col = text_col

    def __len__(self) -> int:
        return self.data.size

    def __getitem__(self, index) -> str:
        data = self.data.iloc[index, :]
        return data[self.text_col]
