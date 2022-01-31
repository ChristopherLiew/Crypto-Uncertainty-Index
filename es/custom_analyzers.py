"""
Custom ES Analyzers for Indexing and Search Queries
"""

from operator import index
from nlp.lexicons import emoji_mappings, crypto_mappings

# Park this under settings['analysis']
reddit_custom_index_analysis = {
    "analyzer": {
        "reddit_index_analyzer": {
            "type": "custom",
            "tokenizer": "standard",
            "char_filter": [
                "html_strip",
                "emoticons"
                ],
            "filter": [
                "lowercase",
                "asciifolding",
                "english_stop",
                "kstem",  # Less aggressive than "stemmer" => Porter Stemmer
            ],
        }
    },
    # Tokenizer
    # "tokenizer": {
    #     "punctuation": {
    #         "type": "pattern",
    #         "pattern": "[ .,!?]"
    #         }
    #     },
    # Before Tokenization
    "char_filter": {
        "emoticons": {
            "type": "mapping",
            "mappings": emoji_mappings.EMOJI_CHAR_MAPPINGS
            }
    },
    # After Tokenization
    "filter": {
        "english_stop": {"type": "stop", "stopwords": "_english_"},
        "crypto_synonyms": {
            "type": "synonym",
            # OR "synonyms_path": "analysis/synonym.txt"
            # (relative to ES config in container)
            # if large number of synonyms
            "synonyms": crypto_mappings.CRYPTO_SYNONYM_MAPPINGS,
        },
    },
}
