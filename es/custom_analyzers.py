"""
Custom ES Analyzers for Indexing and Search Queries
"""

# Park this under settings['analysis']
reddit_custom_index_analysis = {
    "analyzer": {
        "reddit_index_analyzer": {
            "type": "custom",
            "tokenizer": "standard",
            "char_filter": [
                "html_strip"
                ],
            "filter": [
                "lowercase",
                "asciifolding",
                "english_stop"
                ]
            }
        },
    # TBD
    # "tokenizer": {
    #     "punctuation": {
    #         "type": "pattern",
    #         "pattern": "[ .,!?]"
    #         }
    #     },
    'char_filter': {
        'emoticons': {
            'type': 'mapping',
            # TBD
            'mappings': [
                ':) => happy',
                ':( => sad'
                ]
            }
        },
    "filter": {
        "english_stop": {
            "type": "stop",
            "stopwords": "_english_"
            }
        }
    }
