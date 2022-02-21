"""
Construction of Lucey's UCRY Indices
"""


import pandas as pd
from datetime import datetime
from typing import Callable, Union
from es.manager import ESManager
from utils.logger import log
from utils import gen_date_chunks
from pipelines.crypto_index.lucey_keyword_based import keywords as lucey_keywords
from pipelines.crypto_index.topic_modelling_based import lda_keywords, top2vec_keywords


static_es_conn = ESManager()
DATE_FMT = "%Y-%m-%d"


def get_ucry_doc_count(
    index: str,
    start_date: datetime,
    end_date: datetime,
    type: str,
    field: str,
    price_index_q: Callable,
    policy_index_q: Callable,
):
    if type == "price":
        count_query = price_index_q(
            field=field, start_date=start_date, end_date=end_date
        )
    else:
        count_query = policy_index_q(
            field=field, start_date=start_date, end_date=end_date
        )
    res_count = static_es_conn.es_client.count(body=count_query, index=index)
    return res_count["count"]


def construct_ucry_index(
    es_source_index: str,
    start_date: Union[str, datetime],
    end_date: Union[str, datetime],
    granularity: str = "month",
    text_field: str = "full_text",
    type: str = "price",
    prefix: str = "lucey",
) -> pd.DataFrame:

    # Get dates for query
    raw_doc_counts = []

    log.info("Generating date chunks for index construction")
    if isinstance(start_date, str) or isinstance(end_date, str):
        start_date = datetime.strptime(start_date, DATE_FMT)
        end_date = datetime.strptime(end_date, DATE_FMT)
    date_batches = gen_date_chunks(
        start_date=start_date, end_date=end_date, granularity=granularity
    )

    log.info(f"Getting raw counts from ES Index: {es_source_index}")

    # Select price and index queries based on prefix
    if prefix == "lucey":
        price_index_q = lucey_keywords.price_query
        policy_query_q = lucey_keywords.policy_query
    elif prefix == "lda":
        price_index_q = lda_keywords.price_query
        policy_query_q = lda_keywords.policy_query
    elif prefix == "top2vec":
        price_index_q = top2vec_keywords.price_query
        policy_query_q = top2vec_keywords.policy_query
    else:
        raise ValueError(
            "Please provide a valid prefix (i.e. Index Measure): lucey, lda, top2vec."
        )

    # Iterate and get aggregated results
    for s, e in date_batches:
        doc_count = get_ucry_doc_count(
            start_date=s,
            end_date=e,
            type=type,
            index=es_source_index,
            field=text_field,
            price_index_q=price_index_q,
            policy_index_q=policy_query_q,
        )
        raw_doc_counts.append({"start_date": s, "end_date": e, "doc_count": doc_count})
    res_df = pd.DataFrame.from_records(
        raw_doc_counts, columns=["start_date", "end_date", "doc_count"]
    )

    log.info("Computing Index Values")
    mu_1 = res_df["doc_count"].mean()
    sig_1 = res_df["doc_count"].std()
    res_df["index_value"] = ((res_df["doc_count"] - mu_1) / sig_1) + 100

    res_df["type"] = prefix + "-" + type
    return res_df
