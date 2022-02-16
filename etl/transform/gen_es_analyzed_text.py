"""
Processes text from an external source (csv files) using
an elasticsearch index analyzer
"""

import os
import toml
from glob import glob
from tqdm import tqdm
from pathlib import Path
import pandas as pd
from es.manager import ESManager
from elasticsearch.client.indices import IndicesClient
from utils import timer, check_and_create_dir
from utils.logger import log


# Create Indices Client
es_conn = ESManager().es_client
index_client = IndicesClient(es_conn)

ROOT = Path()
config = toml.load(ROOT / "config" / "etl_config.toml")
reddit_config = config["reddit"]
input_data_dir = str(Path(reddit_config["cryptocurrency"]["save_dir"]) / "csv")
output_data_dir = str(
    Path(reddit_config["cryptocurrency"]["save_dir"]).parent / "reddit_analyzed"
)


@timer
def gen_es_analyzed_reddit_topic_corpus(
    es_index: str = "reddit-crypto-topic",
    es_analyzer_name: str = "reddit_topic_model_analyzer",
    input_data_dir: str = input_data_dir,
    output_data_dir: str = output_data_dir,
) -> None:
    """
    Processes raw text data from a CSV using a Pre Defined ES Custom
    Analyzer.

    Args:
        es_index (str): ES Index.
        es_analyzer_name (str): Pre-Defined ES Custom Analyzer
        input_data_dir (str): Source data directory with the following structure:

        data_dir
        |___ subreddit_A.csv
        |___ subreddit_B.csv

        output_data_dir (str): Output data directory.
    """
    log.warning(
        f"Please ensure that {es_analyzer_name} has been created via a PUT request"
    )
    data_files = glob(os.path.join(str(input_data_dir), "*.csv"))
    folder_names = [dir.split("/")[-1].split(".")[0] for dir in data_files]
    log.info(f"Processing text data from {data_files}")
    for name, data in tqdm(zip(folder_names, data_files)):
        log.info(f"Processing data from {data}")
        raw_sr_data = pd.read_csv(data, engine="python").to_dict("records")
        processed_sr_data = []
        for record in tqdm(raw_sr_data, leave=True):
            # Process text with es analyzer
            analyzed_text = index_client.analyze(
                body={
                    "analyzer": f"{es_analyzer_name}",
                    "text": str(record["full_text"]),
                },
                index=es_index,
            )
            record["full_text"] = " ".join(
                [tok["token"] for tok in analyzed_text["tokens"]]
            )
            processed_sr_data.append(record)
        log.info("Data processed! Writing to CSV")
        check_and_create_dir(output_data_dir)
        output_data_path = Path(output_data_dir) / f"{name}_processed_topic.csv"
        pd.DataFrame(processed_sr_data).to_csv(output_data_path, index=False)
    log.info("All data successfully processed and written!")


# Run
gen_es_analyzed_reddit_topic_corpus()

# Test
eth_df = pd.read_csv("etl/raw_data_dump/reddit_analyzed/ethereum_processed_topic.csv")
eth_df.info()
