import os
from pathlib import Path
import gensim
from nlp.topic_models.lda.stream_corpus import StreamingCorpus


os.environ[
    "MALLET_HOME"
] = "/Users/christopherliew/Desktop/Y4S1/HT/crypto_uncertainty_index/Mallet/"
MALLET_PATH = "Mallet/bin/mallet.bat"

corpus = StreamingCorpus(
    [
        "nlp/topic_models/data/processed_reddit_combined/crypto_processed_reddit_combined_10.csv"
    ]
)
num_topics = 100


model_mallet = gensim.models.wrappers.LdaMallet(
    mallet_path=MALLET_PATH,
    corpus=corpus,
    num_topics=num_topics,
    id2word=corpus.corpus_dict,
    random_seed=42,
    workers=7,
    optimize_interval=10,  # Hyperparams Optimization
)


# Get Coherence

# Save Model
model_mallet.save(
    Path("nlp/topic_models/models/lda/lda_mallet_run_2022-02-19 22:00:00")
    / f"lda_mallet_model_{100}.lda"
)
