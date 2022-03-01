"""
Hugging Face Finetuning Script with Weights and Bias Monitoring.

Reference:
1) https://docs.ray.io/en/latest/tune/examples/pbt_transformers.html
2) https://huggingface.co/blog/ray-tune
3) https://deepmind.com/blog/article/population-based-training-neural-networks
"""

# TBD:
# Test functionality
# Train model


import os
import torch
import wandb
import ray
from ray import tune
from ray.tune import CLIReporter
from ray.tune.schedulers import PopulationBasedTraining
from typing import Dict, Optional
from pathlib import Path
from datetime import datetime
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    DataCollatorWithPadding,
    Trainer,
    TrainingArguments,
)
from transformers.integrations import TensorBoardCallback
from nlp.hedge_classifier.utils import (
    compute_clf_metrics,
    get_data_files,
)


# Config
DATE_FMT = "%Y-%m-%dT%H:%M:%S"

# WANDB Set Up
WANDB_RUN_NAME = "hedge-clf-hf-" + datetime.now().strftime(DATE_FMT)

WANDB_PROJECT_TAGS = [
    "HuggingFaceTransformer",
    "HedgeClassifier",
    "TrainingRun",
    "CryptoUncertaintyIndex",
]


# Move to .toml config file
WANDB_DEFAULT_ARGS = {
    "entity": "chrisliew",
    "project": "crypto-hedge-uncertainty",
    "run": WANDB_RUN_NAME,
    "tags": WANDB_PROJECT_TAGS,
}


# Training and Tuning with SOTA PBT
def train_pbt_hf_clf(
    model_name: str,
    train_data_dir: str,
    model_save_dir: str,
    num_labels: int = 2,
    text_col: str = "text",
    wandb_args: Dict[str, str] = WANDB_DEFAULT_ARGS,
    train_data_file_type: str = "csv",
    sample_data_size: Optional[int] = None,
    num_gpus_per_trial: Optional[int] = 0,  # Set to num GPUs available
    smoke_test: bool = False,
    ray_address: Optional[str] = None,
    ray_num_trials: int = 8,  # Number of times to rand sample a point
) -> None:

    # Ray Tune set up
    ray.init(ray_address)  # Defaults to None = Local

    # WandB set up
    wandb.login()
    os.environ["WANDB_LOG_MODEL"] = "true"
    os.environ["WANDB_WATCH"] = "all"
    wandb_args["tags"].append(model_name)

    # Initialize WandB run (Only needed to log artifacts)
    run = wandb.init(
        job_type="training",
        project=wandb_args.get("project", "DummyProjName"),
        name=wandb_args.get("run", "DummyRunName"),
        tags=wandb_args.get("tags", ["DummyTrainTag"]),
        entity=wandb_args["entity"],
    )

    # Check for CUDA
    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

    # Get dataset
    data_files = get_data_files(Path(train_data_dir))
    datasets = load_dataset(train_data_file_type, data_files=data_files)

    # Load Tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    def tokenizer_function(texts):
        return tokenizer(texts[text_col], padding="max_length", truncation=True)

    # Tokenize Datasets
    tokenized_datasets = datasets.map(tokenizer_function, batched=True)

    # Final Datasets
    sample_train_ds = (
        tokenized_datasets["train"].shuffle(seed=42).select(range(sample_data_size))
    )
    sample_test_ds = (
        tokenized_datasets["test"].shuffle(seed=42).select(range(sample_data_size))
    )
    train_ds = tokenized_datasets["train"]
    test_ds = tokenized_datasets["test"]

    # Data Collator with Padding (Dynamic Padding)
    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

    # Download Pretrained Model
    AutoModelForSequenceClassification.from_pretrained(
        model_name, num_labels=num_labels
    )

    # Get Pretrained Modelfor Ray Hyperparam Tuning (must pass as func)
    def get_model() -> AutoModelForSequenceClassification:
        return AutoModelForSequenceClassification.from_pretrained(
            model_name, num_labels=num_labels
        )

    # Training Config
    train_args = TrainingArguments(
        report_to="wandb",
        run_name=wandb_args.get("run", "DummyHFTrainRun"),
        output_dir=model_save_dir,
        load_best_model_at_end=True,
        evaluation_strategy="steps",  # Eval often to prune bad trials
        eval_steps=500,
        save_strategy="steps",
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        num_train_epochs=5,
        fp16=True if device == "cuda" else False,
        learning_rate=2e-5,
        weight_decay=0.01,
        logging_steps=100,
        logging_dir="./nlp/hedge_classifier/logs",
    )

    # Callbacks
    tb_callback = TensorBoardCallback()

    # Trainer
    trainer = Trainer(
        model_init=get_model,
        args=train_args,
        train_dataset=sample_train_ds if sample_data_size else train_ds,
        eval_dataset=sample_test_ds if sample_data_size else test_ds,
        data_collator=data_collator,
        compute_metrics=compute_clf_metrics,
        callbacks=[tb_callback],
    )

    # PBT Hyperparam Search with RayTune
    tune_config = {
        "per_device_train_batch_size": 32,
        "per_device_eval_batch_size": 32,
        "num_train_epochs": tune.choice([2, 3, 4, 5]),
        "max_steps": 1 if smoke_test else -1,  # Used for smoke test.
    }

    scheduler = PopulationBasedTraining(
        time_attr="training_iteration",
        metric="eval_acc",
        mode="max",
        perturbation_interval=1,
        hyperparam_mutations={
            "weight_decay": tune.uniform(0.0, 0.3),
            "learning_rate": tune.uniform(1e-5, 5e-5),
            "per_device_train_batch_size": [16, 32, 64],
        },
    )

    reporter = CLIReporter(
        parameter_columns={
            "weight_decay": "w_decay",
            "learning_rate": "lr",
            "per_device_train_batch_size": "train_bs/gpu",
            "num_train_epochs": "num_epochs",
        },
        metric_columns=["eval_acc", "eval_loss", "epoch", "training_iteration"],
    )

    best_trial = trainer.hyperparameter_search(
        hp_space=lambda _: tune_config,
        backend="ray",
        n_trials=ray_num_trials,  # Check what this means
        resources_per_trial={"cpu": 1, "gpu": num_gpus_per_trial},
        scheduler=scheduler,
        keep_checkpoints_num=1,
        checkpoint_score_attr="training_iteration",
        stop={"training_iteration": 1} if smoke_test else None,
        progress_reporter=reporter,
        local_dir="./nlp/hedge_classifier/ray_results/",
        name="tune_bertweet_pbt",
        log_to_file=True,
    )

    # End WandB Session
    wandb.finish()
    # Serialize Best Trial
    return best_trial


# Test
# if __name__ == "__main__":
#     model_name = "vinai/bertweet-base"
#     train_data_dir = "nlp/hedge_classifier/data/wiki_weasel_clean"
#     model_save_dir = "nlp/hedge_classifier/models"
#     num_labels = 2
#     text_col = "text"
#     wandb_args = WANDB_DEFAULT_ARGS
#     train_data_file_type = "csv"
#     sample_data_size = 1000
#     num_gpus_per_trial = 0
#     smoke_test = False
#     ray_address = None
#     ray_num_trials = 8

#     train_pbt_hf_clf(
# model_name=model_name,
# train_data_dir=train_data_dir,
# model_save_dir=model_save_dir,
# num_labels=num_labels,
# text_col=text_col,
# wandb_args=wandb_args,
# train_data_file_type=train_data_file_type,
# sample_data_size=sample_data_size,
# num_gpus_per_trial=num_gpus_per_trial,
# smoke_test=smoke_test,
# ray_address=ray_address,
# ray_num_trials=ray_num_trials
#     )
