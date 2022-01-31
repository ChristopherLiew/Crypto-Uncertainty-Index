"""
Utility functions and decorators for various general usecases.
"""

import os
import time
from pathlib import Path
from typing import List, Union
from functools import wraps
from datetime import datetime
from arrow import Arrow as arw


def timer(f):
    @wraps(f)
    def func(*args, **kwargs):
        tic = time.time()
        result = f(*args, **kwargs)
        print(f"Function `{f.__name__}` took: {time.time() - tic} seconds")
        return result

    return func


@timer
def gen_date_chunks(
    start_date: datetime,
    end_date: datetime,
    granularity: str = "month",
) -> List[datetime]:
    return [
        (x.datetime, y.datetime)
        for x, y in arw.span_range(granularity, start_date, end_date)
    ]


def check_and_create_dir(filepath: Union[str, Path]) -> None:
    if not os.path.exists(filepath):
        os.makedirs(filepath)
        print(f"Directory created at: {filepath}")
    else:
        print("Directory already exists!")
