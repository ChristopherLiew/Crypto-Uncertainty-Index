"""
Construction of Lucey's UCRY Indices
"""


import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, Any
from es.manager import ESManager
from keywords import (
    UCRY_POLICY_KEYWORDS,
    UCRY_PRICE_KEYWORDS
)

def construct_ucry_index(es_source_index: str,
                         text_field: str,
                         start_date: datetime,
                         end_date: datetime,
                         granularity: str = 'monthly',
                         type: str = 'price'
                         ) -> Dict[str, Any]:
    # Configs
    # Perform aggregation search query
    # Compute index
    # Tidy up data
    pass
