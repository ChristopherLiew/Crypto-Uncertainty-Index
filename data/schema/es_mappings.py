"""
ES Mappings for various data to be stored.
"""

from es.custom_analyzers import reddit_custom_index_analysis

############################
### Reddit Data Mappings ###
############################

# Raw Reddit Crypto Index Mapping
REDDIT_CRYPTO_INDEX_NAME = "reddit-crypto"

reddit_crypto_mapping = {
    "mappings": {
        "properties": {
            # If we use index = False then no inverted index will be built
            # -> Slower searches but Faster Indexing and Less Disk Space
            "id": {"type": "keyword"},  # Not analyzed at point of indexing
            "subreddit": {"type": "keyword"},
            "create_datetime": {"type": "date"},
            "author": {"type": "keyword"},
            "full_text": {"type": "text"},
            "type": {"type": "keyword"},
            "parent_id": {"type": "keyword"}
        }
    }
}


# Test Mapping for Reddit
test_reddit_crypto_mapping = {
    "mappings": {
        "properties": {
            # If we use index = False then no inverted index will be built
            # -> Slower searches but Faster Indexing and Less Disk Space
            "id": {"type": "keyword"},  # Not analyzed at point of indexing
            "subreddit": {"type": "keyword"},
            "create_datetime": {"type": "text"},
            "author": {"type": "keyword"},
            "full_text": {"type": "text"},
            "type": {"type": "keyword"},
            "parent_id": {"type": "keyword"}
        }
    }
}


# Raw Reddit Crypto Index Mapping with Custom Index Analyser
REDDIT_CRYPTO_CUSTOM_INDEX_NAME = "reddit-crypto-custom"

reddit_crypto_custom_mapping = {
    "settings": {
        "analysis": reddit_custom_index_analysis
        },
    "mappings": {
        "properties": {
            "id": {"type": "keyword"},
            "subreddit": {"type": "keyword"},
            "create_datetime": {"type": "date"},
            "author": {"type": "keyword"},
            "full_text": {"type": "text"},
            "type": {"type": "keyword"},
            "parent_id": {"type": "keyword"}
        }
    }
}

# Processed Reddit Data
REDDIT_CRYPTO_PROCESSED_INDEX_NAME = "reddit-crypto-processed"

reddit_crypto_processed_mapping = {
    "mappings": {
        "properties": {
            "id": {"type": "keyword"},
            "subreddit": {"type": "keyword"},
            "create_datetime": {"type": "date"},
            "author": {"type": "keyword"},
            "processed_text": {"type": "text"},
            "type": {"type": "keyword"},
        }
    }
}
