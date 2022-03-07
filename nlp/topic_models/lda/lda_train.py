"""
Training Script for MultiCore Ensemble LDA Model for Reliable Topic
Recovery from the Global Structure.

Ref: https://radimrehurek.com/gensim/auto_examples/tutorials/run_ensemblelda.html#sphx-glr-auto-examples-tutorials-run-ensemblelda-py

We will use topic coherence instead of Perplexity (Log Likelihood) since it is not
strongly correlated with human judgement (As opposed to Gavaldon's 2017 approach)
Ref: http://qpleple.com/perplexity-to-evaluate-topic-models/

For Gensim 3.8.3 there is no Ensemble LDA, we will instead run multiple
Multi-Core LDAs and optimize using topic coherence / log-likelihood.
"""

import json
import multiprocessing as mp
from collections import defaultdict
from typing import Dict, Any, Tuple, Union, Optional
from datetime import datetime
from pathlib import Path
from xmlrpc.client import Boolean
from gensim.models import (
    LdaMulticore,
)
from nlp.topic_models.lda.bigram_corpus import (
    BigramStreamingCorpus,
)
from nlp.topic_models.lda.stream_corpus import (
    StreamingCorpus,
)
from utils import check_and_create_dir
from utils.logger import log


# Assuming 1 core = 1 thread
NUM_CORES = mp.cpu_count()


def train_and_tune_lda(
    raw_data_dir: Union[str, Path],
    gram_level: str = "unigram",
    num_topic_range: Tuple[int, int] = (1, 10),
    num_topic_step: int = 1,
    num_workers: int = NUM_CORES - 1,
    chunksize: Optional[int] = 10000,
    passes: Optional[int] = 1,
    alpha: Optional[Union[str, float]] = "symmetric",
    eta: Optional[float] = None,
    random_state: Optional[int] = 42,
    save_dir: Optional[Union[str, Path]] = Path("nlp/topic_models/models/lda"),
    trained_dict_save_fp: Optional[Union[str, Path]] = None,
    trained_bigram_save_fp: Optional[Union[str, Path]] = None,
    get_perplexity: Optional[bool] = False,
    test_data_dir: Optional[Union[str, Path]] = None,
) -> Dict[int, Any]:
    assert gram_level in ("unigram", "bigram"), ValueError(
        "Gram level must be one of 'Bigram' or 'Unigram'"
    )
    log.info(f"Constructing Streaming Corpus from Data Dir from: {raw_data_dir}")
    # Create save dir
    run_dir = Path(save_dir) / f"lda_run_{datetime.now()}"
    check_and_create_dir(str(run_dir))
    # Pull data and Construct corpus
    file_paths = list(Path(raw_data_dir).rglob("*.csv"))
    if gram_level == "unigram":
        stream_corpus = StreamingCorpus(
            csv_file_paths=file_paths,
            load_from_saved_fp=trained_dict_save_fp,
        )
    else:
        stream_corpus = BigramStreamingCorpus(
            csv_file_paths=file_paths,
            load_from_saved_fp=trained_dict_save_fp,
            load_from_saved_bigram=trained_bigram_save_fp,
        )
    # Create test corpus if necessary
    if get_perplexity:
        log.info(f"Constructing Test Corpus from Test Data Dir: {test_data_dir}")
        test_data_paths = list(Path(test_data_dir).rglob("*.csv"))
        test_corpus = StreamingCorpus(
            csv_file_paths=test_data_paths,
        )
    # Save dictionary to run
    stream_corpus.save_dict(save_fp=run_dir / "dictionary.txt")
    # Store topics and coherence scores
    results = defaultdict(dict)
    # Iterate over topic num
    log.info("Starting LDA model training")
    for num_topics in range(num_topic_range[0], num_topic_range[1] + 1, num_topic_step):
        # Train model
        log.info(f"Training LDA model with {num_topics} number of topics")
        lda = LdaMulticore(
            corpus=stream_corpus,
            num_topics=num_topics,
            id2word=stream_corpus.corpus_dict,
            workers=num_workers,
            chunksize=chunksize,
            passes=passes,
            alpha=alpha,
            eta=eta,
            random_state=random_state,
        )
        # Get UMass Topic Coherence
        log.info(
            f"Getting LDA model UMass with {num_topics} number of topics for Training Data"
        )
        top_topics = lda.top_topics(stream_corpus)
        ave_topic_coherence = sum([t[1] for t in top_topics]) / num_topics
        log.info(
            f"""LDA model with {num_topics} number of
                 topics has a average UMass coherence score
                 of {ave_topic_coherence}"""
        )
        # Get log perplexity on hold out set
        log_perplexity = 'null'
        if get_perplexity:
            log.info("Getting perplexity on Test Data")
            log_perplexity = lda.log_perplexity(test_corpus)
            log.info(f"Log Perplexity on the Test Data set: {log_perplexity}")
        # Save models
        log.info("Saving LDA model")
        lda.save(str(run_dir / f"lda_model_{num_topics}_{ave_topic_coherence}_{log_perplexity}.lda"))
        results[num_topics] = {
            "u_mass": str(ave_topic_coherence),
            "top_topics": str(top_topics),
            "log_perplexity": str(log_perplexity),
        }
    # Save results as JSON
    log.info("Saving results as JSON")
    with open(str(run_dir / "results.json"), 'w') as fp:
        json.dump(results, fp, indent=4)
    log.info(
        f"""Full training loop complete! Saved Dictionary,
             Models and Results can be found at {run_dir}"""
    )
    return results
