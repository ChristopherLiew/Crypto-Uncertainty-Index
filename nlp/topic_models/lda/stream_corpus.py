"""
Class for streaming very large corpus. This assumes that the text being read is already
preprocessed and all we need to do here is build the dictionary and create a streaming corpus
for RAM friendliness.

Ref: https://radimrehurek.com/gensim/auto_examples/core/run_corpora_and_vector_spaces.html#sphx-glr-auto-examples-core-run-corpora-and-vector-spaces-py
"""


from typing import Optional, Set, Union, List
from pathlib import Path
from gensim import corpora
from gensim.utils import tokenize
from gensim.parsing.preprocessing import (
    STOPWORDS,
)
from smart_open import open
from utils.logger import log


# TODO:
# Add in Train - Test Split

# STOPWORD LIST
ENHANCED_STOPWORDS = STOPWORDS.union(["http", "https", "com", "www"])


class StreamingCorpus:
    """
    Memory friendly corpus for Topic Modelling in Gensim.
    """

    def __init__(
        self,
        csv_file_paths: List[Union[str, Path]],
        text_col_idx: int = -1,
        load_from_saved_fp: Optional[Union[str, Path]] = None,
        stop_words: Set[str] = ENHANCED_STOPWORDS,
        min_word_len: int = 2,
    ) -> None:
        """
        Constructor for memory friendly Gensim Corpus.

        Args:
            csv_file_paths (List[Union[str, Path]]): List of file paths to pull raw csv text data from.
            text_col_idx (int, optional): Index of column containing text docs. Defaults to -1.
            load_from_saved_fp (Optional[Union[str, Path]], optional): Filepath to previously saved Dictionary. Defaults to None.
        """
        self.file_paths = csv_file_paths
        self.text_col_idx = text_col_idx
        self.length = 0
        # Initialise tokenizer
        log.info("Constructing Dictionary")
        # Construct memory friendly dictionary
        main_dict = corpora.Dictionary()
        self.corpus_dict = main_dict
        if load_from_saved_fp:
            self.load_dict(load_from_saved_fp)
            log.info(f"Dictionary loaded: {self.corpus_dict}")
        else:
            # Update with additional docs from additional files
            for file_path in csv_file_paths:
                self.corpus_dict.add_documents(
                    [
                        tok
                        for tok in list(tokenize(line.lower().split(",")[text_col_idx]))
                        if tok not in stop_words and len(tok) >= min_word_len
                    ]
                    for line in open(file_path)
                )
                # remove gaps in id sequence after words were removed
                self.corpus_dict.compactify()
                # remove tokens that barely occur or occur frequently
                log.info("Filtering extreme tokens")
                self.corpus_dict.filter_extremes(no_below=20, no_above=0.5)
            log.info(f"Dictionary constructed: {self.corpus_dict}")

    def __iter__(self):
        log.info("Streaming input text to create BOW Corpus")
        # Hacky but reset to 0
        self.length = 0
        for file_path in self.file_paths:
            for line in open(file_path):
                self.length += 1
                # Assume same format as corpus used to build dictionary
                yield self.corpus_dict.doc2bow(
                    list(tokenize(line.lower().split(",")[self.text_col_idx]))
                )
        log.info("End of StreamingCorpus")

    def __len__(self) -> int:
        try:
            return self.__getattribute__("length")
        except AttributeError as e:
            e(
                "Length can only be computed after __iter__\
              has been called on StreamingCorpus object"
            )

    def save_dict(self, save_fp: Union[str, Path]) -> None:
        self.corpus_dict.save_as_text(str(save_fp))

    def load_dict(self, save_fp: Union[str, Path]) -> None:
        self.corpus_dict = self.corpus_dict.load_from_text(str(save_fp))


# Test
# file_paths = list(Path("nlp/topic_models/data/processed_reddit").glob("*.csv"))
# corpus = StreamingCorpus(file_paths)
