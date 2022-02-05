"""
Training Script for rust based GSDMM.
"""

import pandas as pd
import subprocess as sub
from es.manager import ESManager

# Pipeline for Training single GSDMM
# 1) Get raw text (All or stratified sample across time and subreddit)
# 2) -> Preprocess text (Using a custom text processing pipe or ES analysed text)
# 3) -> Pass into GSDMM
# 4) -> Process results into usable format

# Optimizing
# 5) -> Use Genetic algorithm to tune LDA or look at likelihood maximisation


def train_gsdmm_rust(data: pd.DataFrame):
    pass
