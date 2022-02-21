POST /reddit-crypto-custom/_search?pretty
{
    "query": {
        "range": {
            "create_datetime": {
                "gte": "2014-01-01",
                "lte": "2021-12-31"
            }
        }
    },
    "aggs": {
        "count_per_week": {
            "date_histogram": {
                "field": "create_datetime",
                "calendar_interval": "week"
            },
            "aggs": {
                "subreddit_count": {
                    "terms": {
                        "field": "subreddit"
                    }
                }
            }
        }
    }
}
}

POST /reddit-crypto-custom/_analyze
{
    "analyzer": "reddit_index_analyzer",
    "text": "🐋's are dumping BTC<p> @elonmusk is dumping his coins! I'm so <b>ànnoyed</b>:/ urrrgggghhhhhhhhhhhhhrhhhhhhhhhhhhhhhhhhrhhhhhh</p>"
}
