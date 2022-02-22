"""
Hugging Face Finetuning Script with Weights and Bias Monitoring.
"""


import os
import torch
import wandb
from typing import (
    Dict,
    Optional
)
from datetime import datetime
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    DataCollatorWithPadding,
    Trainer,
    TrainingArguments
)
from transformers.integrations import TensorBoardCallback
from nlp.hedge_classifier.utils import (
    compute_clf_metrics,
    get_data_files,
)


# Config
DATE_FMT = "%Y-%m-%dT%H:%M:%S"

# WANDB Set Up
WANDB_RUN_NAME = (
    "hedge-clf-hf-"
    + datetime.now().strftime(DATE_FMT)
)

WANDB_PROJECT_TAGS = [
    "HuggingFaceTransformer",
    "HedgeClassifier",
    "TrainingRun",
    "CryptoUncertaintyIndex"
]


# Move to .toml config file
WANDB_DEFAULT_ARGS = {
    'entity': 'chrisliew',
    'project': 'crypto-hedge-uncertainty',
    'run': WANDB_RUN_NAME,
    'tags': WANDB_PROJECT_TAGS
}


# Training
def train_hf_clf(
    model_name: str,
    train_data_dir: str,
    model_save_dir: str,
    num_labels: int = 2,
    text_col: str = "text",
    wandb_args: Dict[str, str] = WANDB_DEFAULT_ARGS,
    train_data_file_type: str = "csv",
    sample_data_size: Optional[int] = None
) -> None:
    # WandB set up
    wandb.login()
    os.environ['WANDB_LOG_MODEL'] = 'true'
    os.environ['WANDB_WATCH'] = 'all'
    wandb_args['tags'].append(model_name)
    # Initialize WandB run
    run = wandb.init(
        job_type='training',
        project=wandb_args.get('project', 'DummyProjName'),
        name=wandb_args.get('run', 'DummyRunName'),
        tags=wandb_args.get('tags', ['DummyTrainTag']),
        entity=wandb_args['entity']
    )
    # Check for CUDA
    device = (
        torch.device("cuda")
        if torch.cuda.is_available()
        else torch.device("cpu")
    )
    # Get dataset
    data_files = get_data_files(train_data_dir)
    datasets = load_dataset(
        train_data_file_type,
        data_files=data_files
    )
    # Load Tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    def tokenizer_function(texts):
        return tokenizer(
            texts[text_col],
            padding="max_length",
            truncation=True)

    # Tokenize Datasets
    tokenized_datasets = (
        datasets
        .map(tokenizer_function, batched=True)
    )
    # Final Datasets
    sample_train_ds = (
        tokenized_datasets["train"]
        .shuffle(seed=42)
        .select(range(sample_data_size))
    )
    sample_test_ds = (
        tokenized_datasets["test"]
        .shuffle(seed=42)
        .select(range(sample_data_size))
    )
    train_ds = tokenized_datasets["train"]
    test_ds = tokenized_datasets["test"]
    # Data Collator with Padding (Dynamic Padding)
    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)
    # Load Pretrained Model
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=num_labels
    )
    # Training Config
    train_args = TrainingArguments(
        report_to='wandb',
        run_name=wandb_args.get('run', 'DummyHFTrainRun'),
        output_dir=model_save_dir,
        load_best_model_at_end=False,
        evaluation_strategy='epoch',
        save_strategy='epoch',
        per_device_train_batch_size=32,
        per_device_eval_batch_size=32,
        num_train_epochs=5,
        fp16= True if device == 'cuda' else False,
        learning_rate=2e-5,
        weight_decay=0.01,
        logging_steps=100,
    )
    # Callbacks
    tb_callback = TensorBoardCallback()
    # Trainer
    trainer = Trainer(
        model=model,
        args=train_args,
        train_dataset=sample_train_ds if sample_data_size else train_ds,
        eval_dataset=sample_test_ds if sample_data_size else test_ds,
        data_collator=data_collator,
        compute_metrics=compute_clf_metrics,
        callbacks=[tb_callback]
    )
    # Train model
    trainer.train()
    # Eval model
    trainer.evaluate()
    # End WandB Session
    wandb.finish()


# Test
train_hf_clf()
