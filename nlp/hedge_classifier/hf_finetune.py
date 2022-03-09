"""
Hugging Face Finetuning Script with Weights and Bias Monitoring.

Reference:
1) https://docs.ray.io/en/latest/tune/examples/pbt_transformers.html
2) https://huggingface.co/blog/ray-tune
3) https://deepmind.com/blog/article/population-based-training-neural-networks
4) https://ruanchaves.medium.com/integrating-ray-tune-hugging-face-transformers-and-w-b-172c07ce2854
"""

# TODO:
# 1. Fix WandB integration [see: https://github.com/wandb/client/issues/3045]
# 2. Train on SageMaker
# 3. Refactor file paths to save results

import json
import os
from typing import Dict, Optional
from pathlib import Path
from datetime import datetime
import torch
# import wandb
import ray
from ray import tune
from ray.tune import CLIReporter
# from ray.tune.logger import DEFAULT_LOGGERS
# from ray.tune.integration.wandb import (
#     WandbLoggerCallback,
#     WandbLogger,
# )
from ray.tune.examples.pbt_transformers.utils import build_compute_metrics_fn
from ray.tune.schedulers import PopulationBasedTraining
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    DataCollatorWithPadding,
    TrainingArguments,
)
from transformers.trainer import Trainer
from nlp.hedge_classifier.utils import (
    get_data_files,
)
from utils.logger import log


# Config
DATE_FMT = "%Y-%m-%dT%H:%M:%S"
# WANDB Set Up (Abstract out to TOML file)
WANDB_RUN_NAME = "PBT-Ray-Hedge-Clf-" + datetime.now().strftime(DATE_FMT)
WANDB_PROJECT_TAGS = [
    "HuggingFaceTransformer",
    "HedgeClassifier",
    "TrainingRun",
    "CryptoUncertaintyIndex",
]
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
    train_data_file_type: str = "csv",
    sample_data_size: Optional[int] = None,
    wandb_args: Dict[str, str] = WANDB_DEFAULT_ARGS,
    num_cpus_per_trial: Optional[int] = 4,
    num_gpus_per_trial: Optional[int] = 1,  # Set to num GPUs available
    ray_address: Optional[str] = None,
    ray_num_trials: int = 8,  # Number of times to rand sample a point
    smoke_test: bool = False,
) -> None:

    # Ray Tune set up
    log.info("Setting up Ray Tune")
    ray.init(ray_address)  # Defaults to None = Local

    # WandB set up
    # log.info("Setting up Weights U Biases")
    # wandb.login()
    # os.environ["WANDB_LOG_MODEL"] = "true"
    # os.environ["WANDB_WATCH"] = "all"
    # wandb_args["tags"].append(model_name)

    # Initialize WandB run (Only needed to log artifacts)
    # wandb.init(
    #     job_type="training",
    #     project=wandb_args.get("project", "DummyProjName"),
    #     name=wandb_args.get("run", "DummyRunName"),
    #     tags=wandb_args.get("tags", ["DummyTrainTag"]),
    #     entity=wandb_args["entity"],
    # )

    # Check for GPUs
    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

    log.info("Preparing Datasets")

    # Get dataset
    data_files = get_data_files(Path(train_data_dir))
    datasets = load_dataset(train_data_file_type, data_files=data_files)

    # Load Tokenizer (Set Normalization=True if tweets are raw to handle emojis etc)
    tokenizer = AutoTokenizer.from_pretrained(model_name, normalization=True)

    def tokenizer_function(texts):
        return tokenizer(texts[text_col], padding="max_length", truncation=True)

    log.info("Tokenizing Datasets")
    # Tokenize Datasets
    tokenized_datasets = datasets.map(tokenizer_function, batched=True)

    # Final + Sampled Datasets
    if sample_data_size:
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

    log.info(f"Loading {model_name} from cache or Hugging Face hub")
    # Download Pretrained Model
    AutoModelForSequenceClassification.from_pretrained(
        model_name, num_labels=num_labels
    )

    # Get Pretrained Modelfor Ray Hyperparam Tuning (must pass as func)
    def get_model() -> AutoModelForSequenceClassification:
        model = AutoModelForSequenceClassification.from_pretrained(
            model_name, num_labels=num_labels
        )
        return model

    # Training Config
    train_args = TrainingArguments(
        report_to=None,
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

    # Trainer
    trainer = Trainer(
        model_init=get_model,
        args=train_args,
        train_dataset=sample_train_ds if sample_data_size else train_ds,
        eval_dataset=sample_test_ds if sample_data_size else test_ds,
        data_collator=data_collator,
        compute_metrics=build_compute_metrics_fn("rte"),  # See: Glue Output Modes (rte == classification)
    )

    # PBT Hyperparam Search with RayTune
    def hp_space_fn(*args, **kwargs):
        config = {
            "per_device_train_batch_size": 32,
            "per_device_eval_batch_size": 32,
            "warmup_steps": tune.choice([50, 100, 500]),
            "num_train_epochs": tune.choice([2, 3, 4, 5]),
            "weight_decay": tune.uniform(0.0, 0.3),
            "learning_rate": tune.choice([1e-5, 2e-5, 5e-5]),
            "max_steps": 1 if smoke_test else -1,
        }
        return config

    scheduler = PopulationBasedTraining(
        time_attr="training_iteration",
        metric="eval_acc",
        mode="max",
        perturbation_interval=1,  # Perturb after 1 training iteration
    )

    reporter = CLIReporter(
        parameter_columns={
            "warmup_steps": "warmup",
            "weight_decay": "w_decay",
            "learning_rate": "lr",
            "per_device_train_batch_size": "train_bs/gpu",
            "num_train_epochs": "num_epochs",
        },
        metric_columns=[
            "eval_acc",
            "eval_loss",
            "epoch",
            "training_iteration",
        ],
    )

    log.info("Running Population Based Training - Hyperparams Search")
    best_trial = trainer.hyperparameter_search(
        hp_space=hp_space_fn,
        direction="maximize",
        backend="ray",
        n_trials=ray_num_trials,
        resources_per_trial={
            "cpu": num_cpus_per_trial,
            "gpu": num_gpus_per_trial
            },
        scheduler=scheduler,
        keep_checkpoints_num=1,
        checkpoint_score_attr="training_iteration",
        stop={"training_iteration": 1} if smoke_test else None,
        progress_reporter=reporter,
        local_dir="./nlp/hedge_classifier/hyper_tuning/ray_results/",
        name=f"tune_hf_pbt_{datetime.now().strftime(DATE_FMT)}",
        log_to_file=True,
        # loggers=DEFAULT_LOGGERS + (WandbLogger,),
    )

    log.info("Population Based Training completed!")
    best_params = json.dumps(best_trial.hyperparameters, indent=4)
    log.info(f"Best Hyperparams: {best_params}")
    log.info(f"Serializing Best Params to Current Directory: {os.getcwd()}")
    with open(
        f"./nlp/hedge_classifier/hyper_tuning/pbt_best_params/best_params_{datetime.now().strftime(DATE_FMT)}.json", "w"
    ) as fp:
        json.dump(best_params, fp, indent=4)

    # End WandB Session
    # wandb.finish()


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
