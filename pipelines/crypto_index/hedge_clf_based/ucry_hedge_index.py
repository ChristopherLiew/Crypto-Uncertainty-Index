"""
Constructs Hedge Based Cryptocurrency Uncertainty Index
"""

from typing import List, Any, Dict, Union
from tqdm import tqdm
from pathlib import Path
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
)
from transformers.pipelines import pipeline
from transformers.pipelines.base import Pipeline
from torch.utils.data import Dataset
from nlp.hedge_classifier.huggingface.reddit_dataset import (
    RedditInferenceDataset,
)

# TODO:
# 1. Pull data in batches from Elasticsearch / Locally
# 2. Pass them through HF inference
# 3. Compute Index Values for given date batch
# 4. Push index value to Postgres

# Config (Move to TOML)
MODEL_CHECKPOINT = "nlp/hedge_classifier/models/best_pbt_bertweet/checkpoint"
MODEL_NAME = "vinai/bertweet-base"


def construct_hedge_index(
    hf_model_name: str,
    inf_data_dir: Union[str, Path],
    hf_model_ckpt: Optional[Union[str, Path]] = None,
) -> None:
    if hf_model_ckpt
    pass
