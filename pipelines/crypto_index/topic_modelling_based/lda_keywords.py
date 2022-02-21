"""
ES Query containing keywords for constructing LDA based Index

We use LDA with K = 10 and take the top 5 terms for Topic 6
Lambda = 0.6 see: https://nlp.stanford.edu/events/illvi2014/papers/sievert-illvi2014.pdf
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
                    # Uncertainty terms
                    {
                        "bool": {
                            "should": [
                                {"wildcard": {f"{field}": "uncertain*"}},
                                {
                                    "terms": {
                                        f"{field}": [
                                            "skeptical",
                                            "annoyed",
                                            "hesitant",
                                            "uneasy",
                                            "undecided",
                                        ]
                                    }
                                },
                            ]
                        }
                    },
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
                    # Uncertainty terms
                    {
                        "bool": {
                            "should": [
                                {"wildcard": {f"{field}": "uncertain*"}},
                                {
                                    "terms": {
                                        f"{field}": [
                                            "skeptical",
                                            "annoyed",
                                            "hesitant",
                                            "uneasy",
                                            "undecided",
                                        ]
                                    }
                                },
                            ]
                        }
                    },
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
