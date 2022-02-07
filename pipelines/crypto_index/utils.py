"""
[TBD] UCRY Index Related Util Functions
"""

import toml
from pathlib import Path
from datetime import datetime
from etl.schema.es_mappings import REDDIT_CRYPTO_CUSTOM_INDEX_NAME
from pipelines.crypto_index.lucey_keyword_based.ucry_indices import construct_ucry_index

# Config
DATE_FMT = "%Y-%m-%d"
config = toml.load(Path() / "config" / "etl_config.toml")
START_DATE, END_DATE = (
    datetime.strptime(config["reddit"]["cryptocurrency"]["start_date"], DATE_FMT),
    datetime.strptime(config["reddit"]["cryptocurrency"]["end_date"], DATE_FMT),
)


# Utils to pull index data from ES and write to csv
# CREATE CRYPTO INDEX UTILS TO WRITE OUT INDEX VALUES TO CSV
lucey_price_index = construct_ucry_index(
    es_source_index=REDDIT_CRYPTO_CUSTOM_INDEX_NAME,
    start_date=START_DATE,
    end_date=END_DATE,
    type="price",
    granularity="week",
    text_field="full_text",
)


lucey_policy_index = construct_ucry_index(
    es_source_index=REDDIT_CRYPTO_CUSTOM_INDEX_NAME,
    start_date=START_DATE,
    end_date=END_DATE,
    type="policy",
    granularity="week",
    text_field="full_text",
)

lucey_price_index.to_csv(
    "/Users/christopherliew/Desktop/Y4S1/HT/crypto_uncertainty_index/pipelines/crypto_index/index_data/ucry_lucey_price.csv",
    index=False,
)
lucey_policy_index.to_csv(
    "/Users/christopherliew/Desktop/Y4S1/HT/crypto_uncertainty_index/pipelines/crypto_index/index_data/ucry_lucey_policy.csv",
    index=False,
)
