"""
Data classes for KuCoin Data.
"""

from pydantic.dataclasses import dataclass
from pydantic import Field
from datetime import datetime


@dataclass
class KuCoinCandle:
    datetime: datetime
    open: float = Field(None, description="Opening price")
    close: float = Field(None, description="Closing price")
    high: float = Field(None, description="Highest price")
    low: float = Field(None, description="Lowest price")
    amount: float = Field(None, description="Transaction amount")
    volume: float = Field(None, description="Transaction volume")

    def __post_init__(self) -> None:
        print(self.datetime)
        datetime_int = int(self.datetime)
        self.datetime = datetime.fromtimestamp(datetime_int)
