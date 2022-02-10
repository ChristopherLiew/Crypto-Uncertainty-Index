"""
Processes text from an external source (csv files) using
an elasticsearch index analyzer
"""

from es.manager import ESManager


def gen_es_analyzed_reddit_corpus(
    es_index, es_analyzer, input_data_dir, output_data_dir
) -> None:
    # 1) Load data from input data dir
    # 2) Process documents from each files
    #   - Load file
    #   - For each document pass it into the analyzer for custom index
    #   - Obtain analyzer results (Non-tokenized)
    # 3) Repeat for each subreddit directory
    # 4) Write out as csv files
    pass
