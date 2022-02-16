"""
Training Script for Top2Vec Algorithm.
"""

from multiprocessing import cpu_count
from typing import List, Union, Optional
import polars as pl
from top2vec import Top2Vec
from pathlib import Path
from utils import check_and_create_dir
from utils.logger import log

NUM_CORES = cpu_count()


def train_top2vec(
    data: Union[str, Path] = Path("nlp/topic_models/data/processed_reddit/crypto_processed_reddit_combined.csv"),
    min_count: int = 50,
    speed: str = "learn",
    num_workers: int = NUM_CORES - 1,
    embedding_model: Optional[str] = None,
    model_save_dir: Union[str, Path] = Path('.')
) -> None:
    assert num_workers <= NUM_CORES, "Insufficient cores!"
    assert embedding_model in (
        "doc2vec",
        "sentence-transformers",
        "universal-sentence-encoder",
        "universal-sentence-encoder-multilingual",
        "distiluse-base-multilingual-cased",
    )
    log.info("Loading corpus")
    train_data = (
        pl.read_csv(data)
        .to_series(0)
        .to_list()
    )
    log.info("Training Top2Vec model using {} workers and {} as embedding model")
    model = Top2Vec(
        documents=train_data,
        min_count=min_count,
        speed=speed,
        workers=num_workers,
        embedding_model=None if embedding_model == "doc2vec" else embedding_model,
        use_corpus_file=True if embedding_model == "doc2vec" else False,
    )
    log.info("Saving model ...")
    model_save_path = model_save_dir if isinstance(model_save_dir, Path) else Path(model_save_dir)
    check_and_create_dir(model_save_path)
    model.save(model_save_path / f"top2vec_{speed}_{embedding_model}")
    log.info(f"Model saved to {model_save_path}")
