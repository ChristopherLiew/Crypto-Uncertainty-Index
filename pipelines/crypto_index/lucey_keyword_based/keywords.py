"""
ES Query containing keywords for constructing Lucey Et Al's Index
"""

from datetime import datetime
from typing import Dict, Any


def price_query(field: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:

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
    return count_query


def policy_query(
    field: str, start_date: datetime, end_date: datetime
) -> Dict[str, Any]:

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
    return count_query
