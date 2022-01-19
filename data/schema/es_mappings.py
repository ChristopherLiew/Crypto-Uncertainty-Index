"""
ES Mappings for various data.
"""

############################
### Reddit Data Mappings ###
############################

# Reddit Crypto Index Mapping
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
