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

import tempfile
import multiprocessing as mp
import click_spinner
from collections import defaultdict
from typing import Tuple, Union, Optional
from datetime import datetime
from pathlib import Path
from gensim import corpora
from gensim.models import (
    LdaMulticore,
    CoherenceModel,
)
from nlp.topic_models.lda.stream_corpus import (
    StreamingCorpus,
)
from utils import check_and_create_dir
from utils.logger import log


# Assuming 1 core = 1 thread
NUM_CORES = mp.cpu_count()


def train_and_tune_LDA(
    raw_data_dir: Union[str, Path],
    num_topic_range: Tuple[int, int] = (100, 500),
    num_topic_step: int = 100,
    num_workers: int = NUM_CORES - 1,
    chunksize: Optional[int] = 10000,
    passes: Optional[int] = 1,
    alpha: Optional[float] = 'symmetric',
    eta: Optional[float] = None,
    random_state: Optional[int] = 42,
    # coherence_score_type: Optional[str] = 'u_mass',
    save_dir: Optional[Union[str, Path]] = Path('../models/lda')
) -> None:
    log.info("Constructing Streaming Corpus from Data Dir")
    # Pull data and Construct corpus
    file_paths = list(Path(str(raw_data_dir)).rglob("*.csv"))
    stream_corpus = StreamingCorpus(csv_file_paths=file_paths)
    # Store best lda model and all results
    topic_coherence_scores = defaultdict(lambda _: "No Score")
    # Create save dir
    run_dir = save_dir / f"lda_run_{datetime.now()}"
    check_and_create_dir(str(run_dir))
    # Iterate over topic num
    for num_topics in range(
        num_topic_range[0],
        num_topic_range[1],
        num_topic_step
    ):
        # Train model
        log.info(f"Training LDA model with {num_topics} number of topics")
        with click_spinner.spinner():
            lda = LdaMulticore(
                corpus=stream_corpus,
                num_topics=num_topics,
                id2word=stream_corpus.corpus_dict,
                workers=num_workers,
                chunksize=chunksize,
                passes=passes,
                alpha=alpha,
                eta=eta,
                random_state=random_state
            )
        # Get topic coherence
        log.info(f"Running Coherence model on LDA model with {num_topics} number of topics")
        with click_spinner.spinner():
            # coherence_model = CoherenceModel(
            #     model=lda,
            #     corpus=stream_corpus,
            #     dictionary=stream_corpus.corpus_dict,
            #     coherence=coherence_score_type
            # )
            # coherence_score = coherence_model.get_coherence()
            top_topics = lda.top_topics(stream_corpus)
            ave_topic_coherence = sum([t[1] for t in top_topics]) / num_topics
        log.info(f"""LDA model with {num_topics} number of
                 topics has a average UMass coherence score
                 of {ave_topic_coherence}""")

        # Save models
        log.info("Saving LDA model")
        with tempfile.NamedTemporaryFile(
            prefix=f'lda-model-{num_topics}-{ave_topic_coherence}',
            suffix='.lda',
            delete=False
        ) as tmp:
            lda.save(run_dir / tmp)

        topic_coherence_scores[f'lda_{num_topics}'] = ave_topic_coherence

    log.info(f"Full training loop complete! Saved models can be found at {run_dir}")


# Test
