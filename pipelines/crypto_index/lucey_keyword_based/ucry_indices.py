"""
Construction of Lucey's UCRY Indices
"""


import pandas as pd
from datetime import datetime
from typing import Union
from es.manager import ESManager
from utils.logger import log
from utils import gen_date_chunks


static_es_conn = ESManager()
DATE_FMT = "%Y-%m-%d"


def get_ucry_doc_count(
    index: str, start_date: datetime, end_date: datetime, type: str, field: str
):
    if type == "price":
        count_query = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "terms": {
                                f"{field}": [
                                    "bitcoin",
                                    "ethereum",
                                    "ripple",
                                    "litecoin",
                                    "tether",
                                    "cryptocurrency",
                                    "cryptocurrencies",
                                ]
                            }
                        },
                        {"wildcard": {f"{field}": "pric*"}},
                        {"wildcard": {f"{field}": "uncertain*"}},
                        {
                            "range": {
                                "create_datetime": {
                                    "gte": str(start_date.date()),
                                    "lte": str(end_date.date()),
                                }
                            }
                        },
                    ]
                }
            }
        }
    else:
        count_query = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "terms": {
                                f"{field}": [
                                    "bitcoin",
                                    "ethereum",
                                    "ripple",
                                    "litecoin",
                                    "tether",
                                    "cryptocurrency",
                                    "cryptocurrencies",
                                ]
                            }
                        },
                        {
                            "terms": {
                                f"{field}": [
                                    "regulator",
                                    "regulators",
                                    "central bank",
                                    "government",
                                    "fed",
                                    "feds",
                                ]
                            }
                        },
                        {"wildcard": {f"{field}": "uncertain*"}},
                        {
                            "range": {
                                "create_datetime": {
                                    "gte": str(start_date.date()),
                                    "lte": str(end_date.date()),
                                }
                            }
                        },
                    ]
                }
            }
        }
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
    # Iterate and get aggregated results
    for s, e in date_batches:
        doc_count = get_ucry_doc_count(
            start_date=s, end_date=e, type=type, index=es_source_index, field=text_field
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
