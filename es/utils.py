"""
Utility functions for Elasticsearch related usecases.
"""

from typing import Union, List, Dict, Any
import pandas as pd
import polars as pl
from datetime import datetime
from elasticsearch_dsl.response import Response


# Globals
# Date Format
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"


# Data Processing
def es_reddit_to_df(results: Union[Response, List[Dict[str, Any]]],
                    input_type: str = 'dsl',
                    output_type: str = 'pandas') -> pd.DataFrame:

    assert input_type in ('dsl', 'es'),\
        ValueError('Input type must be one of "dsl" or "es"')

    if input_type == 'es':
        results_list = [
           {
               "id": hit['_source']['id'],
               "create_datetime": datetime.strptime(
                   hit['_source']['create_datetime'],
                   DATETIME_FORMAT),
               "subreddit": hit['_source']['subreddit'],
               "full_text": hit['_source']['full_text']
            } for hit in results
        ]
    elif input_type == 'dsl':
        results_list = [
            {
                "id": hit.id,
                "create_datetime": datetime.strptime(
                    hit.create_datetime,
                    DATETIME_FORMAT),
                "subreddit": hit.subreddit,
                "full_text": hit.full_text
            } for hit in results
        ]

    pandas_df = pd.DataFrame.from_records(results_list)
    if output_type.lower() == "pandas":
        return pandas_df
    if output_type.lower() == "polars":
        return pl.DataFrame(pandas_df)  # Slow method
    else:
        raise ValueError("output_type must be one of 'pandas' or 'polars'")
