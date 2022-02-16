"""
CLI interface for NLP modelling and processes
"""

from curses import raw
from numpy import save
from torch import chunk
import typer
from pathlib import Path
from typing import Optional, Union, Tuple
from nlp.topic_models.lda.lda_train import NUM_CORES, train_and_tune_lda

# Create Typer App
nlp_app = typer.Typer(name="NLP")


# Topic Modelling
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
):
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
