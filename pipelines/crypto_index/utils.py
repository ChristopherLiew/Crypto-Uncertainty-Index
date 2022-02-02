"""
[TBD] UCRY Index Related Util Functions
"""
from etl.schema.es_mappings import REDDIT_CRYPTO_CUSTOM_INDEX_NAME
from pipelines.crypto_index.lucey_keyword_based.ucry_indices import (
    construct_ucry_index
)
from config.reddit_data_cfg import CRYPTO_REDDIT_DATE_RANGE
START_DATE, END_DATE = CRYPTO_REDDIT_DATE_RANGE.values()


# Utils to pull index data from ES and write to csv
# CREATE CRYPTO INDEX UTILS TO WRITE OUT INDEX VALUES TO CSV
lucey_price_index = construct_ucry_index(
    es_source_index=REDDIT_CRYPTO_CUSTOM_INDEX_NAME,
    start_date=START_DATE,
    end_date=END_DATE,
    type="price",
    granularity="week",
    text_field="full_text"
)


lucey_policy_index = construct_ucry_index(
    es_source_index=REDDIT_CRYPTO_CUSTOM_INDEX_NAME,
    start_date=START_DATE,
    end_date=END_DATE,
    type="policy",
    granularity="week",
    text_field="full_text"
)

lucey_price_index.to_csv('/Users/christopherliew/Desktop/Y4S1/HT/crypto_uncertainty_index/pipelines/crypto_index/index_data/ucry_lucey_price.csv', index=False)
lucey_policy_index.to_csv('/Users/christopherliew/Desktop/Y4S1/HT/crypto_uncertainty_index/pipelines/crypto_index/index_data/ucry_lucey_policy.csv', index=False)
