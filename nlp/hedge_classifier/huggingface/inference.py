"""
Reddit Inference (Torch) Dataset for Downstream Use.
"""
from __future__ import annotations
import polars as pl
from tqdm import tqdm
from time import strptime
from datetime import datetime
from torch.utils.data import Dataset
from typing import Union, Optional
from pathlib import Path


class RedditInferenceDataset(Dataset):
    """
    Dataset for Inference on Reddit Data extracted from PushShift.io
    """

    def __init__(
        self,
        data_source: Union[str, Path, pl.DataFrame],
        nrows: Optional[float] = None,
        text_col: Optional[str] = "full_text",
    ) -> None:
        """
        Constructor for the Inference Dataset

        Args:
            data_source (Union[str, Path, pl.DataFrame]): Either a Polars
            DataFrame or Path to a Directory of CSVs to load data from.
            nrows (Optional[float], optional): Number of rows to load, if None
            loads all. Defaults to None.
            text_col (Optional[str], optional): Text column name to use for
            downstream processing.

        Raises:
            ValueError: If invalid data_source.
        """

        self.text_col = text_col

        if isinstance(data_source, pl.DataFrame):
            self.data = data_source

        elif isinstance(data_source, str) or isinstance(data_source, Path):
            data_fps = list(Path(data_source).rglob("*.csv"))
            self.data = pl.concat(
                [pl.read_csv(fp, nrows=nrows) for fp in tqdm(data_fps)],
                how="vertical",
            ).drop_nulls()
        else:
            raise ValueError("Please provide a valid value for data!")

    def date_subset(
        self,
        start_date: Union[str, datetime],
        end_date: Union[str, datetime],
        date_col: str = "created",
    ) -> RedditInferenceDataset:
        """
        Returns a new dataframe with a subset of the original data based on a
        given date range.

        Args:
            start_date (Union[str, datetime]): Start date.
            end_date (Union[str, datetime]): End date.
            date_col (str, optional): Name of Data Column. Defaults to
            'created'.

        Returns:
            RedditInferenceDataset: Subsetted Polars DataFrame based
            on Date range.
        """

        subset_data = self.data.filter(
            pl.col(date_col).is_between(start=start_date, end=end_date)
        )
        return self.__class__(subset_data, text_col=self.text_col)

    def __len__(self) -> int:
        return self.data.shape[0]

    def __getitem__(self, index) -> str:
        data = self.data[index]
        return data[self.text_col][0]
