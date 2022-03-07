"""
Utils for classifier training.
"""

import wandb
import numpy as np
from typing import (
    Callable,
    Dict,
)
from datasets import load_metric
from transformers import EvalPrediction
from pathlib import Path


# Load Metrics
acc_metric = load_metric("accuracy")
f1_metric = load_metric("f1")
prec_metric = load_metric("precision")
rec_metric = load_metric("recall")


def compute_clf_metrics(eval_pred: EvalPrediction) -> Callable[[EvalPrediction], Dict]:

    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    metrics = dict()

    metrics["accuracy"] = acc_metric.compute(predictions=predictions, references=labels)
    metrics["f1"] = f1_metric.compute(
        predictions=predictions, references=labels, average="macro"
    )
    metrics["precision"] = prec_metric.compute(
        predictions=predictions, references=labels, average="macro"
    )
    metrics["recall"] = rec_metric.compute(
        predictions=predictions, references=labels, average="macro"
    )
    return metrics


# Train-Test only
def get_data_files(data_dir_root: Path, format: str = "csv") -> Dict[str, str]:
    data_files = dict()
    train_path, test_path = (
        f"train.{format}",
        f"test.{format}",
    )
    data_files["train"] = str(data_dir_root / train_path)
    data_files["test"] = str(data_dir_root / test_path)
    return data_files
