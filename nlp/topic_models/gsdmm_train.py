"""
Training Script for rust based GSDMM.
"""

from datetime import datetime
import os
from pathlib import Path
from typing import Union
import subprocess as sub
from nlp.topic_models.lda.stream_corpus import StreamingCorpus
from utils.logger import log

# NOTE:
# Doesn't converge for reddit corpus


def train_gsdmm_rust(
    data_fp: Union[str, Path],
    num_topics: int = 100,
    alpha: float = 0.1,
    beta: float = 0.1,
    max_iter: int = 1000,
    vocab_save_fp: Union[str, Path] = "nlp/topic_models/data/gsdmm_reddit/vocab.txt",
    res_save_fp: Union[str, Path] = "nlp/topic_models/models/gsdmm",
    gsdmm_bin: Union[str, Path] = "gsdmm-rust/target/release/gsdmm",
) -> None:
    log.info(f"Constructing suitable dataset and vocab from {data_fp}")
    # 1) Data processing (Start with sample and)
    # - Get all data (Sample)
    data = StreamingCorpus([data_fp])
    # - Get all data vocab and write out
    data.save_dict(vocab_save_fp)
    # 2) Run subprocess
    print(os.getcwd())
    res_save_fp = str(
        Path(str(res_save_fp))
        / f"gsdmm_res_{num_topics}_{max_iter}_{alpha}_{beta}_{datetime.now()}_"
    )
    log.info(
        f"""Running GSDMM-Rust with the following params:
             K = {num_topics}, a = {alpha}, b = {beta} and m = {max_iter}"""
    )
    sub.run(
        [
            f"{gsdmm_bin}",
            f"{data_fp}",
            f"{vocab_save_fp}",
            f"{res_save_fp}",
            "-a",
            f"{alpha}",
            "-b",
            f"{beta}",
            "-m",
            f"{max_iter}",
            "-k",
            f"{num_topics}",
        ]
    )
    log.info("Completed running GSDMM Rust")


# Test
# train_gsdmm_rust(
#     data_fp="nlp/topic_models/data/processed_reddit_combined/crypto_processed_reddit_combined_5.csv",
#     num_topics=100,
#     max_iter=250)

# sub.run(
#     ['gsdmm-rust/target/release/gsdmm',
#      'nlp/topic_models/data/processed_reddit_combined/crypto_processed_reddit_combined_5.csv',
#      'nlp/topic_models/data/gsdmm_reddit/vocab.txt',
#      'nlp/topic_models/models/gsdmm/gsdmm_res_100_10000_0.1_0.1_2022-02-19 14:43:46.726175_',
#      '-a', '0.1', '-b', '0.1', '-m', '10000', '-k', '100']
# )
