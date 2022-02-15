"""
Class for streaming very large corpus. This assumes that the text being read is already
preprocessed and all we need to do here is build the dictionary and create a streaming corpus
for RAM friendliness.

Ref: https://radimrehurek.com/gensim/auto_examples/core/run_corpora_and_vector_spaces.html#sphx-glr-auto-examples-core-run-corpora-and-vector-spaces-py
"""


from typing import Union, List
from pathlib import Path
from gensim import corpora
from gensim.utils import tokenize
from smart_open import open
from utils import timer
from utils.logger import log

# TODO:
# 1) Add in Bigrams and Trigrams


class StreamingCorpus:
    @timer
    def __init__(self,
                 csv_file_paths: List[Union[str, Path]],
                 text_col_idx: int = -1
                 ) -> None:

        self.file_paths = csv_file_paths
        self.text_col_idx = text_col_idx

        # Initialise tokenizer
        log.info("Constructing Dictionary")
        # Construct memory friendly dictionary
        main_dict = corpora.Dictionary()
        # Update with additional docs from additional files
        for file_path in csv_file_paths:
            main_dict.add_documents(
                list(tokenize(line.lower().split(',')[text_col_idx])) for
                line in open(file_path)
            )

        # remove gaps in id sequence after words were removed
        main_dict.compactify()
        log.info("Filtering extreme tokens")
        main_dict.filter_extremes(no_below=20, no_above=0.5)

        self.corpus_dict = main_dict
        log.info(f"Dictionary constructed: {main_dict}")

    def __iter__(self):

        log.info("Streaming input text to create BOW Corpus")

        for file_path in self.file_paths:
            for line in open(file_path):
                # Assume same format as corpus used to build dictionary
                yield self.dictionary.doc2bow(
                    line.lower().split(',')[self.text_col_idx]
                )

        log.info("End of StreamingCorpus")


# Test
# ROOT = Path("nlp/topic_models/data/processed_reddit/")
# file_paths = [
#     ROOT / "Bitcoin_processed_topic.csv",
#     ROOT / "BitcoinMarkets_processed_topic.csv",
#     ROOT / "CryptoCurrencyTrading_processed_topic.csv"
# ]
# test_corpus = StreamingCorpus(csv_file_paths=file_paths)
# list(ROOT.rglob('*.csv'))
