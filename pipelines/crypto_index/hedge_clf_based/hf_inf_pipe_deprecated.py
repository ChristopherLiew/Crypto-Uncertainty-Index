"""
[DEPRACATED] Inference Pipeline for Hugging Face Hedge Classifier.

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
from nlp.hedge_classifier.huggingface.inference import (
    RedditInferenceDataset,
)
from utils.logger import log

# TODO:
# 1. Change from inf_Dataset to List[str] data
# 2. At UCRY_HEDGE build dataset and query out only what
# is needed by week in batches


# Default Values move to TOML
MODEL_CHECKPOINT = "nlp/hedge_classifier/models/best_model"
MODEL_NAME = "vinai/bertweet-base"
RESULT_SAVE_DIR = "nlp/hedge_classifier/data/hedge_inference_results"

TOKENIZER_KWARGS = {
    "padding": True,
    "truncation": True,
}


def run_inference(
    inf_dataset: Union[Dataset, DataLoader],
    model_name: str = MODEL_NAME,
    model_ckpt_dir: Union[str, Path] = MODEL_CHECKPOINT,
    res_save_dir: Union[str, Path] = RESULT_SAVE_DIR,
    tokenizer_kwargs: Dict[str, bool] = TOKENIZER_KWARGS,
) -> None:

    null_count = 0
    if isinstance(inf_dataset, Dataset):
        log.info("Constructing Data Loader")
        inf_dataset = DataLoader(inf_dataset)

    log.info("Loading Hugging Face artefacts ...")
    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        normalization=True,
    )
    model = AutoModelForSequenceClassification.from_pretrained(model_ckpt_dir)
    pipe = pipeline(
        task="text-classification",
        model=model,
        tokenizer=tokenizer,
    )

    with open(Path(res_save_dir) / "results.csv", "w", newline="") as csvf:
        fieldnames = ["text", "label", "score"]
        writer = csv.DictWriter(csvf, fieldnames=fieldnames)
        writer.writeheader()
        log.info("Performing inference on dataset ...")
        for doc in tqdm(inf_dataset):
            try:
                out = pipe(doc, **tokenizer_kwargs)[0]
                label, score = (out.get("label", "None"), out.get("score", "None"))
                label = 1 if label == "LABEL_1" else 0
                writer.writerow({"text": doc[0], "label": label, "score": score})
            except ValueError:
                writer.writerow({"text": doc[0], "label": -1, "score": -1.0})
                null_count += 1
        log.info(f"Inference complete! Results saved to {res_save_dir}")


# Test
data = RedditInferenceDataset(data_dir=Path("nlp/topic_models/data/processed_reddit"))
results = run_inference(inf_dataset=data)
