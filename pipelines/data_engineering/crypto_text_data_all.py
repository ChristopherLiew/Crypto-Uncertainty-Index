"""
Extract all relevant reddit crypto data and insert to ES.
"""

from typing import List
from datetime import datetime
from config.reddit_data_cfg import (
    CRYPTO_REDDIT_DATE_RANGE,
    CRYPTO_SUBREDDITS
)

def elt_crypto_reddit_data(subreddits: List[str],
                           start_date: datetime,
                           end_date: datetime):
    # Extract
    # Load
    pass
