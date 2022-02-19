"""
Training Script for rust based GSDMM.
"""

from datetime import datetime
from pathlib import Path
from typing import Union
import subprocess as sub
from nlp.topic_models.lda.stream_corpus import StreamingCorpus
from utils.logger import log

# TODO:
# 1) Test
# 2) Start with small sample and tune


def train_gsdmm_rust(data_fp: Union[str, Path],
                     num_topics: int = 100,
                     alpha: float = 0.1,
                     beta: float = 0.1,
                     max_iter: int = 10000,
                     vocab_save_fp: Union[str, Path] = "nlp/topic_models/data/gsdmm_reddit/vocab.txt",
                     res_save_fp: Union[str, Path] = "nlp/topic_models/models/gsdmm",
                     gsdmm_bin: Union[str, Path] = "./gsdmm-rust/target/release/gsdmm"
                     ) -> None:
    log.info(f"Constructing suitable dataset and vocab from {data_fp}")
    # 1) Data processing (Start with sample and)
    # - Get all data (Sample)
    data = StreamingCorpus([data_fp])
    # - Get all data vocab and write out
    data.save_dict(vocab_save_fp)
    # 2) Run subprocess
    res_save_fp = str(
        Path(str(res_save_fp))
        / f"gsdmm_res_{num_topics}_{max_iter}_{alpha}_{beta}_{datetime.now()}_"
    )
    log.info(f"""Running GSDMM-Rust with the following params:
             K = {num_topics}, a = {alpha}, b = {beta} and m = {max_iter}""")
    sub.run(
        f"""
        {gsdmm_bin} {data_fp}
        {vocab_save_fp} {res_save_fp}
        -a {alpha} -b {beta} -m {max_iter}
        -k {num_topics}
        """
    )
    log.info("Completed running GSDMM Rust")
