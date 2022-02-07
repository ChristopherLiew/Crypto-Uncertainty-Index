"""
Custom ES Analyzers for Indexing and Search Queries
"""

from nlp.text_preprocessing import (
    emoji_mappings,
    crypto_mappings,
    common_mappings
)

# Park this under settings['analysis']
reddit_custom_index_analysis = {
    "analyzer": {
        "reddit_index_analyzer": {
            "type": "custom",
            "tokenizer": "standard",
            "char_filter": [
                "html_strip",
                "emoticons",
                "crypto_lex",
                "general_en_contractions",
                "reddit_handle_replace",
                "twitter_handle_replace",
                "lengthy_char_replace",
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
            "mappings": emoji_mappings.EMOJI_CHAR_MAPPINGS,
        },
        "general_en_contractions": {
            "type": "mapping",
            "mappings": common_mappings.COMMON_CONTRACTION_MAPPINGS,
        },
        "reddit_handle_replace": {
            "type": "pattern_replace",
            "pattern": "/u/[A-Za-z0-9_-]+",
            "replacement": "__reddit_handle__",
        },
        "twitter_handle_replace": {
            "type": "pattern_replace",
            "pattern": "/(^|[^@\\w])@(\\w{1,15})\\b/",
            "replacement": "__twitter_handle__",
        },
        "lengthy_char_replace": {
            "type": "pattern_replace",
            "pattern": "\\b\\w{50,}\\b",
            "replacement": "",
        },
    },
    # After Tokenization
    "filter": {
        "english_stop": {"type": "stop", "stopwords": "_english_"},
        "crypto_synonym": {
            "type": "synonym",
            "synonyms": crypto_mappings.CRYPTO_SYNONYM_MAPPINGS,
        },
    },
}
