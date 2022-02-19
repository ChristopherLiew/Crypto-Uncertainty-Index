"""
CLI interface for NLP modelling and processes
"""


import typer
import multiprocessing as mp
from typing import Optional, Tuple
from nlp.topic_models.lda.lda_train import train_and_tune_lda
from nlp.topic_models.top2vec_train import train_top2vec

# Config
NUM_CORES = mp.cpu_count()

# Create Typer App
nlp_app = typer.Typer(name="NLP")


# Topic Modelling
@nlp_app.command(
    name="train-Top2Vec",
    help="Trains Top2Vec on a given corpus",
)
def run_train_top2vec(
    data: str = typer.Option(
        "nlp/topic_models/data/processed_reddit_combined/crypto_processed_reddit_combined_20.csv",
        help="Corpus data",
    ),
    min_count: int = typer.Option(
        50, help="Minimum number of counts a word should have to be included"
    ),
    speed: str = typer.Option(
        "learn",
        help="Learning speed. One of learn, fast-learn or deep-learn"
    ),
    num_workers: int = typer.Option(
        NUM_CORES - 1, help="Number of CPU threads to train model"
    ),
    embedding_model: str = typer.Option("doc2vec", help="Embedding model"),
    umap_low_mem: bool = typer.Option(False, help="Whether to use low mem for UMAP"),
    model_save_dir: str = typer.Option(
        "nlp/topic_models/models/top2vec", help="Model save directory"
    ),
) -> None:
    train_top2vec(
        data=data,
        min_count=min_count,
        speed=speed,
        num_workers=num_workers,
        embedding_model=embedding_model,
        model_save_dir=model_save_dir,
        umap_low_mem=umap_low_mem
    )


@nlp_app.command(
    name="train-and-tune-LDA",
    help="Train multiple iterations of LDA for various Num Topics (K)",
)
def run_train_and_tune_lda(
    raw_data_dir: str = typer.Option(
        "nlp/topic_models/data/processed_reddit",
        help="Directory containing csv files with processed data (sans tokenization)",
    ),
    num_topic_range: Tuple[int, int] = typer.Option(
        (10, 50), help="Lower and upper bound of K to try out"
    ),
    num_topic_step: int = typer.Option(
        10, help="Step size to increment K by within topic range"
    ),
    num_workers: Optional[int] = typer.Option(
        NUM_CORES - 1, help="Number of workers (CPU cores) to use for parallelization"
    ),
    chunksize: Optional[int] = typer.Option(10000, help="Size of training batches"),
    passes: Optional[int] = typer.Option(
        1, help="Number of passes through the training corpus"
    ),
    alpha: Optional[str] = typer.Option(
        "symmetric", help="Alpha val for a priori topic - document distribution"
    ),
    eta: Optional[float] = typer.Option(None, help="Eta value. See Gensim docs"),
    random_state: Optional[int] = typer.Option(42, help="Random seed"),
    save_dir: Optional[str] = typer.Option(
        "nlp/topic_models/models/lda",
        help="Where to save relevant dict, model data for each run",
    ),
    dict_save_dir: Optional[str] = typer.Option(
        None,
        help="Location of saved dictionary for corpus. Specify to use pre-constructed dict.",
    ),
) -> None:
    train_and_tune_lda(
        raw_data_dir=raw_data_dir,
        num_topic_range=num_topic_range,
        num_topic_step=num_topic_step,
        num_workers=num_workers,
        chunksize=chunksize,
        passes=passes,
        alpha=alpha,
        eta=eta,
        random_state=random_state,
        save_dir=save_dir,
        dict_save_dir=dict_save_dir,
    )
