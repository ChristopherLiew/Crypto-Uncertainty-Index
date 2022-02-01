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
                "general_en_contractions"
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
            },
        "crypto_lex": {
            "type": "mapping",
            "mappings": crypto_mappings.CRYPTO_LEXICON_MAPPINGS,
        },
        "general_en_contractions": {
            "type": "mapping",
            "mappings": common_mappings.COMMON_CONTRACTION_MAPPINGS
        }
    },
    # After Tokenization
    "filter": {
        "english_stop": {
            "type": "stop",
            "stopwords": "_english_"
            }
    },
}
