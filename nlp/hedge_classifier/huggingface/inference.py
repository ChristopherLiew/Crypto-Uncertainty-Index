"""
Inference Pipeline for Hugging Face Hedge Classifier.

Ref for Batch Streaming:
https://huggingface.co/docs/transformers/v4.17.0/en/main_classes/pipelines#transformers.TextClassificationPipeline
"""

from typing import List, Any, Dict
from tqdm import tqdm
from pathlib import Path
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
)
from transformers.pipelines import pipeline
from torch.utils.data import Dataset
from nlp.hedge_classifier.huggingface.reddit_dataset import (
    RedditInferenceDataset,
)


# Config (Move to TOML)
MODEL_CHECKPOINT = "nlp/hedge_classifier/models/best_pbt_bertweet/checkpoint"
MODEL_NAME = "vinai/bertweet-base"


# Load Pretrained Models + Tokenizers
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, normalization=True)

model = AutoModelForSequenceClassification.from_pretrained(MODEL_CHECKPOINT)

pipe = pipeline(task="text-classification", model=model, tokenizer=tokenizer)


# Test Data (Create Batches when processing ES data)
data = RedditInferenceDataset(data_dir=Path("nlp/topic_models/data/processed_reddit"))


# Inference (DEBUG Value Errror text input must of type str)
def run_inference(
    pipeline: pipeline,
    inf_dataset: Dataset,
    truncation: bool = True,
    padding: bool = True,
) -> List[Dict[str, Any]]:
    tokenizer_kwargs = {
        "padding": padding,
        "truncation": truncation,
    }
    results = []
    for i, out in enumerate(tqdm(pipeline(inf_dataset, **tokenizer_kwargs))):
        print(f"{i}: {inf_dataset.__getitem__(i)}")
        results.append(out)
    return results


# Test
results = run_inference(pipeline=pipe, inf_dataset=data)
