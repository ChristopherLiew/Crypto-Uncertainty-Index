"""
Constructs Hedge Based Cryptocurrency Uncertainty Index
"""

import pandas as pd
import numpy as np
from tqdm import tqdm
from pathlib import Path
from typing import Optional, Union
from datetime import datetime
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
)
from transformers.pipelines import pipeline
from nlp.hedge_classifier.huggingface.inference import (
    RedditInferenceDataset,
)
from utils.logger import log
from utils import gen_date_chunks

# Config
DATE_FMT = "%Y-%m-%d"
TOKENIZER_KWARGS = {
    "padding": True,
    "truncation": True,
}


def construct_hedge_index(
    data_source: Union[str, Path],
    start_date: Union[str, datetime],
    end_date: Union[str, datetime],
    hf_model_name: str,
    hf_model_ckpt: Optional[str] = None,
    name: str = "hedge",
    granularity: str = "week",
) -> pd.DataFrame:
    # Load All Data
    log.info(f"Constructing Dataset from: {data_source}")
    red_df = RedditInferenceDataset(data_source=data_source)
    # Set up HF pipeline
    log.info(
        f"Setting up Hugging Face Pipeline using: {hf_model_ckpt if hf_model_ckpt else hf_model_name}"
    )
    tokenizer = AutoTokenizer.from_pretrained(
        hf_model_name,
        normalization=True,
    )
    model = AutoModelForSequenceClassification.from_pretrained(
        hf_model_ckpt if hf_model_ckpt else hf_model_name
    )
    pipe = pipeline(
        task="text-classification",
        model=model,
        tokenizer=tokenizer,
    )
    # Get weekly batches
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, DATE_FMT)
        end_date = datetime.strptime(end_date, DATE_FMT)

    date_chunks = gen_date_chunks(
        start_date=start_date, end_date=end_date, granularity=granularity
    )
    # Store All weekly counts
    ucry_hedge_raw = []
    # Subset out relevant data from each weekly date chunk
    log.info(
        f"Constructing Hedge based UCRY index from start={start_date} to end={end_date} ..."
    )
    for start, end in tqdm(date_chunks):
        start_, end_ = (
            datetime.strftime(start, DATE_FMT),
            datetime.strftime(end, DATE_FMT),
        )
        weekly_data = red_df.date_subset(start_, end_)
        # Perform inference using HF pipeline
        hedge_pipe = pipe(weekly_data, **TOKENIZER_KWARGS)
        res = [
            1 if res.get("label", None) == "LABEL_1" else 0
            for res in tqdm(iter(hedge_pipe), leave=True)
        ]
        # Store results for this week
        ucry_hedge_raw.append(
            {
                "type": name,
                "start_date": start_,
                "end_date": end_,
                "doc_count": np.sum(res),
            }
        )
    log.info("Computing Index Values ..")
    ucry_hedge_df = pd.DataFrame(ucry_hedge_raw)
    mu_1 = ucry_hedge_df["doc_count"].mean()
    sig_1 = ucry_hedge_df["doc_count"].std()
    ucry_hedge_df["index_value"] = ((ucry_hedge_df["doc_count"] - mu_1) / sig_1) + 100
    return ucry_hedge_df


# Test
# START_DATE = "2014-01-01"
# END_DATE = "2014-06-30"
# MODEL_CHECKPOINT = "nlp/hedge_classifier/models/best_model"
# MODEL_NAME = "vinai/bertweet-base"


# test_res = construct_hedge_index(
#     data_source="nlp/topic_models/data/processed_reddit",
#     start_date=START_DATE,
#     end_date=END_DATE,
#     hf_model_name=MODEL_NAME,
#     hf_model_ckpt=MODEL_CHECKPOINT,
#     name='bertweet-hedge'
# )
