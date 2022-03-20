"""
Inference Pipeline for Hugging Face Hedge Classifier.

Ref for Batch Streaming:
https://huggingface.co/docs/transformers/v4.17.0/en/main_classes/pipelines#transformers.TextClassificationPipeline
"""
# TODO:
# Port over to Inference Pipeline after Sanity Check

import csv
from typing import Dict, Union
from tqdm import tqdm
from pathlib import Path
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
)
from transformers.pipelines import pipeline
from torch.utils.data import Dataset
from torch.utils.data.dataloader import DataLoader
from nlp.hedge_classifier.huggingface.reddit_inference_dataset import (
    RedditInferenceDataset,
)

# Config (Move to TOML)
MODEL_CHECKPOINT = "nlp/hedge_classifier/models/best_model"
MODEL_NAME = "vinai/bertweet-base"
RESULT_SAVE_DIR = "nlp/hedge_classifier/data/hedge_inference_results"


# Load Pretrained Models + Tokenizers
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, normalization=True)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_CHECKPOINT)
pipe = pipeline(task="text-classification", model=model, tokenizer=tokenizer)

tokenizer_kwargs = {
    "padding": True,
    "truncation": True,
}


# Inference (DEBUG Value Errror text input must of type str)
def run_inference(
    pipeline: pipeline,
    inf_dataset: Union[Dataset, DataLoader],
    tokenizer_kwargs: Dict[str, bool] = tokenizer_kwargs,
    res_save_dir: Union[str, Path] = RESULT_SAVE_DIR,
) -> None:
    null_count = 0
    if isinstance(inf_dataset, Dataset):
        inf_dataset = DataLoader(inf_dataset)
    with open(Path(res_save_dir) / "results.csv", "w", newline="") as csvf:
        fieldnames = ["text", "label", "score"]
        writer = csv.DictWriter(csvf, fieldnames=fieldnames)
        writer.writeheader()
        for doc in tqdm(inf_dataset):
            try:
                out = pipeline(doc, **tokenizer_kwargs)[0]
                label, score = (out.get("label", "None"), out.get("score", "None"))
                label = 1 if label == "LABEL_1" else 0
                writer.writerow({"text": doc[0], "label": label, "score": score})
            except ValueError:
                writer.writerow({"text": doc[0], "label": -1, "score": -1.0})
                null_count += 1
    print(f"Number of Invalid Docs: {null_count}")


# Test
data = RedditInferenceDataset(data_dir=Path("nlp/topic_models/data/processed_reddit"))
results = run_inference(pipeline=pipe, inf_dataset=data)
