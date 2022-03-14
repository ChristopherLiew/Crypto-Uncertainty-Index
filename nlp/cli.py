"""
CLI interface for NLP modelling and processes
"""

import typer
import multiprocessing as mp
from typing import Optional, Tuple
from nlp.topic_models.lda.lda_train import train_and_tune_lda
from nlp.topic_models.top2vec_train import train_top2vec
from nlp.hedge_classifier.huggingface.pbt_transformer import train_pbt_hf_clf
from nlp.hedge_classifier import gradio_app

# Config
NUM_CORES = mp.cpu_count()

# Create Typer App
nlp_app = typer.Typer(name="NLP")


####################
# Hedge Classifier #
####################


@nlp_app.command(
    name="hedge-clf-demo", help="Launches a Gradio app for hedge classification demo."
)
def run_hedge_clf_demo():
    gradio_app.run_app()


@nlp_app.command(
    name="pbt-hedge-clf",
    help="Finetunes Hugging Face classifier using SOTA population based training",
)
def run_train_and_tune_hf_clf(
    model_name: str = typer.Option(
        "vinai/bertweet-base", help="Base huggingface hub transformer to finetune on."
    ),
    train_data_dir: str = typer.Option(
        "nlp/hedge_classifier/data/wiki_weasel_clean",
        help="Data directory containing csv train and test data for finetuning and eval in specified format.",
    ),
    model_save_dir: str = typer.Option(
        "nlp/hedge_classifier/models", help="Model save directory location."
    ),
    sample_data_size: int = typer.Option(
        None, help="Amount of train and test data to use as a subsample for testing."
    ),
    num_cpus_per_trial: int = typer.Option(4, help="Number of CPUs to use per trial"),
    num_gpus_per_trial: int = typer.Option(1, help="Number of GPUs to use per trial."),
    smoke_test: bool = typer.Option(False, help="Whether to run a smoke test."),
    ray_address: str = typer.Option(
        None, help="Ray address location. If None uses Local."
    ),
    ray_num_trials: int = typer.Option(
        8, help="Number of times to Randomly Sample a point in the Params Grid"
    ),
) -> None:

    train_pbt_hf_clf(
        model_name=model_name,
        train_data_dir=train_data_dir,
        model_save_dir=model_save_dir,
        sample_data_size=sample_data_size,
        num_cpus_per_trial=num_cpus_per_trial,
        num_gpus_per_trial=num_gpus_per_trial,
        smoke_test=smoke_test,
        ray_address=ray_address,
        ray_num_trials=ray_num_trials,
    )


###################
# Topic Modelling #
###################
@nlp_app.command(
    name="train-t2v",
    help="Trains Top2Vec on a given corpus",
)
def run_train_top2vec(
    data: str = typer.Option(
        "nlp/topic_models/data/processed_reddit_combined/crypto_processed_reddit_combined_10.csv",
        help="Corpus data",
    ),
    min_count: int = typer.Option(
        50, help="Minimum number of counts a word should have to be included"
    ),
    speed: str = typer.Option(
        "learn", help="Learning speed. One of learn, fast-learn or deep-learn"
    ),
    num_workers: int = typer.Option(
        NUM_CORES - 1, help="Number of CPU threads to train model"
    ),
    embedding_model: str = typer.Option("doc2vec", help="Embedding model"),
    umap_low_mem: bool = typer.Option(False, help="Whether to use low mem for UMAP"),
    hdb_min_cluster_size: int = typer.Option(100, help="HDBSCAN min cluster size"),
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
        umap_low_mem=umap_low_mem,
        hdb_min_cluster_size=hdb_min_cluster_size,
    )


@nlp_app.command(
    name="train-multi-lda",
    help="Train multiple iterations of LDA for various Num Topics (K)",
)
def run_train_and_tune_lda(
    raw_data_dir: str = typer.Option(
        # 100%: nlp/topic_models/data/processed_reddit
        "nlp/topic_models/data/processed_reddit_train_test/train",
        help="Directory containing csv files with processed data (sans tokenization)",
    ),
    gram_level: str = typer.Option("unigram", help="Unigram or Bigrams"),
    num_topic_range: Tuple[int, int] = typer.Option(
        (1, 10), help="Lower and upper bound of K to try out"
    ),
    num_topic_step: int = typer.Option(
        1, help="Step size to increment K by within topic range"
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
    trained_dict_save_fp: Optional[str] = typer.Option(
        None,
        help="Location of saved dictionary for corpus. Specify to use pre-constructed dict.",
    ),
    trained_bigram_save_fp: Optional[str] = typer.Option(
        None,  # "nlp/topic_models/models/bigram/reddit_bigram_full",
        help="Bigram Model Save directory",
    ),
    get_perplexity: Optional[bool] = typer.Option(
        True,
        help="Whether to compute log perplexity on each model on a held out test set.",
    ),
    test_data_dir: Optional[str] = typer.Option(
        "nlp/topic_models/data/processed_reddit_train_test/test",
        help="File path to test data dir to compute log perplexity on.",
    ),
) -> None:

    train_and_tune_lda(
        raw_data_dir=raw_data_dir,
        gram_level=gram_level,
        num_topic_range=num_topic_range,
        num_topic_step=num_topic_step,
        num_workers=num_workers,
        chunksize=chunksize,
        passes=passes,
        alpha=alpha,
        eta=eta,
        random_state=random_state,
        save_dir=save_dir,
        trained_dict_save_fp=trained_dict_save_fp,
        trained_bigram_save_fp=trained_bigram_save_fp,
        get_perplexity=get_perplexity,
        test_data_dir=test_data_dir,
    )
