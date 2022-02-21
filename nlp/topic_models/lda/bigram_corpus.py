"""
Class for streaming very large corpus. This assumes that the text being read is already
preprocessed and all we need to do here is build the dictionary and create a streaming corpus
for RAM friendliness.

Ref: https://radimrehurek.com/gensim/auto_examples/core/run_corpora_and_vector_spaces.html#sphx-glr-auto-examples-core-run-corpora-and-vector-spaces-py
"""


from typing import Optional, Union, List
from pathlib import Path
from gensim import corpora
from gensim.utils import tokenize
from gensim.models import Phrases
from gensim.models.phrases import Phraser
from smart_open import open
from utils.logger import log
from nlp.topic_models.lda.stream_corpus import StreamingCorpus


class BigramStreamingCorpus(StreamingCorpus):
    """
    Memory friendly bigram corpus for Topic Modelling in Gensim.
    """

    def __init__(
        self,
        csv_file_paths: List[Union[str, Path]],
        bigram_min_count: int = 20,
        text_col_idx: int = -1,
        vocab_no_below: int = 20,
        vocab_no_above: float = 0.5,
        bigram_save_fp: Optional[
            Union[str, Path]
        ] = "nlp/topic_models/models/bigram/reddit_bigram_full",
        load_from_saved_bigram: Optional[Union[str, Path]] = None,
        load_from_saved_fp: Optional[Union[str, Path]] = None,
    ) -> None:

        self.bigram_min_count = bigram_min_count
        self.bigram_save_fp = bigram_save_fp
        self.file_paths = csv_file_paths
        self.text_col_idx = text_col_idx
        self.length = 0

        # Construct Bigram Corpus
        if load_from_saved_bigram is not None:
            log.info(f"Loading pre-trained Phraser model from {load_from_saved_bigram}")
            self.bigram_model = Phraser.load(load_from_saved_bigram)
        else:
            assert (
                bigram_save_fp
            ), "Please provide a save dir for Bigram model or a pre-trained model"
            self.__construct_bigrams()

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
                    self.bigram_model[line.lower().split(",")[text_col_idx]]
                    for line in open(file_path)
                )
                # remove gaps in id sequence after words were removed
                self.corpus_dict.compactify()
                # remove tokens that barely occur or occur frequently
                log.info("Filtering extreme tokens")
                self.corpus_dict.filter_extremes(
                    no_below=vocab_no_below, no_above=vocab_no_above
                )
            log.info(f"Dictionary constructed: {self.corpus_dict}")

    def __iter__(self):
        log.info("Streaming input text to create BOW Corpus")
        self.length = 0
        for file_path in self.file_paths:
            for line in open(file_path):
                self.length += 1
                # Assume same format as corpus used to build dictionary
                yield self.corpus_dict.doc2bow(
                    list(tokenize(line.lower().split(",")[self.text_col_idx]))
                )
        log.info("End of StreamingCorpus")

    def __construct_bigrams(self) -> None:
        log.info("Creating Bigram Corpus")
        bigram = Phrases(min_count=self.bigram_min_count)
        for file_path in self.file_paths:
            bigram.add_vocab(
                line.lower().split(",")[self.text_col_idx] for line in open(file_path)
            )
        self.bigram_model = Phraser(bigram)
        log.info("Saving Bigram Model")
        self.bigram_model.save(self.bigram_save_fp)
