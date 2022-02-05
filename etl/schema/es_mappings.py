"""
ES Mappings for various data to be stored.
"""


##################################
### Uncertainty Index Mappings ###
##################################
LUCEY_UNCERTAINTY_INDEX_NAME = "lucey-ucry"

# Standardised Mapping for Uncertainty Indices
ucry_index_mapping = {
    "mappings": {
        "properties": {
            "type": {"type": "keyword"},
            "start_date": {"type": "date"},
            "end_date": {"type": "keyword"},
            "doc_count": {"type": "integer"},
            "index_value": {"type": "float"}
        }
    }
}


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
            "parent_id": {"type": "keyword"},
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
            "parent_id": {"type": "keyword"},
        }
    }
}


# Raw Reddit Crypto Index Mapping with Custom Index Analyser
REDDIT_CRYPTO_CUSTOM_INDEX_NAME = "reddit-crypto-custom"

reddit_crypto_custom_mapping = {
    "settings": {
        "number_of_shards": 5,
        "number_of_replicas": 1,
        "analysis": {
            "analyzer": {
                "reddit_index_analyzer": {
                    "type": "custom",
                    "char_filter": [
                        "html_strip",
                        "emoticons",
                        "general_en_contractions",
                        "reddit_handle_replace",
                        "twitter_handle_replace",
                        "lengthy_char_replace"
                        ],
                    "filter": [
                        "lowercase",
                        "asciifolding",
                        "crypto_synonym",
                        "english_stop",
                        "kstem"
                        ],
                    "tokenizer": "standard"
                    }
                },
            "char_filter": {
                "emoticons": {
                    "type": "mapping",
                    "mappings": [
                        ":) => happy",
                        ":( => sad",
                        "\ud83d\udc0b => whale",
                        ":/ => 'Skeptical, annoyed, undecided, uneasy or hesitant'",
                        "%) => 'Drunk or confused'"
                        ]
                    },
                "general_en_contractions": {
                    "type": "mapping",
                    "mappings": [
                        "ain't => am not",
                        "aren't => are not",
                        "can't => cannot",
                        "can't've => cannot have",
                        "'cause => because",
                        "could've => could have",
                        "couldn't => could not",
                        "couldn't've => could not have",
                        "didn't => did not",
                        "doesn't => does not",
                        "don't => do not",
                        "hadn't => had not",
                        "hadn't've => had not have",
                        "hasn't => has not",
                        "haven't => have not",
                        "he'd => he had",
                        "he'd've => he would have",
                        "he'll => he will",
                        "he'll've => he shall have",
                        "he's => he is",
                        "how'd => how did",
                        "how'd'y => how do you",
                        "how'll => how will",
                        "how's => how has",
                        "I'd => I had",
                        "I'd've => I would have",
                        "I'll => I will",
                        "I'll've => I will have",
                        "I'm => I am",
                        "I've => I have",
                        "isn't => is not",
                        "it'd => it had",
                        "it'd've => it would have",
                        "it'll => it will",
                        "it'll've => it will have",
                        "it's => it is",
                        "let's => let us",
                        "ma'am => madam",
                        "mayn't => may not",
                        "might've => might have",
                        "mightn't => might not",
                        "mightn't've => might not have",
                        "must've => must have",
                        "mustn't => must not",
                        "mustn't've => must not have",
                        "needn't => need not",
                        "needn't've => need not have",
                        "o'clock => of the clock",
                        "oughtn't => ought not",
                        "oughtn't've => ought not have",
                        "shan't => shall not",
                        "sha'n't => shall not",
                        "shan't've => shall not have",
                        "she'd => she would",
                        "she'd've => she would have",
                        "she'll => she will",
                        "she'll've => she will have",
                        "she's => she is",
                        "should've => should have",
                        "shouldn't => should not",
                        "shouldn't've => should not have",
                        "so've => so have",
                        "so's => so as",
                        "that'd => that would",
                        "that'd've => that would have",
                        "that's => that is",
                        "there'd => there had",
                        "there'd've => there would have",
                        "there's => there is",
                        "they'd => they would",
                        "they'd've => they would have",
                        "they'll => they will",
                        "they'll've => they will have",
                        "they're => they are",
                        "they've => they have",
                        "to've => to have",
                        "wasn't => was not",
                        "we'd => we would",
                        "we'd've => we would have",
                        "we'll => we will",
                        "we'll've => we will have",
                        "we're => we are",
                        "we've => we have",
                        "weren't => were not",
                        "what'll => what will",
                        "what'll've => what will have",
                        "what're => what are",
                        "what's => what is",
                        "what've => what have",
                        "when's => when is",
                        "when've => when have",
                        "where'd => where did",
                        "where's => where is",
                        "where've => where have",
                        "who'll => who will",
                        "who'll've => who will have",
                        "who's => who is",
                        "who've => who have",
                        "why's => why is",
                        "why've => why have",
                        "will've => will have",
                        "won't => will not",
                        "won't've => will not have",
                        "would've => would have",
                        "wouldn't => would not",
                        "wouldn't've => would not have",
                        "y'all => you all",
                        "y'all'd => you all would",
                        "y'all'd've => you all would have",
                        "y'all're => you all are",
                        "y'all've => you all have",
                        "you'd => you would",
                        "you'd've => you would have",
                        "you'll => you will",
                        "you'll've => you will have",
                        "you're => you are",
                        "you've => you have"
                        ]
                    },
                "lengthy_char_replace": {
                    "type": "pattern_replace",
                    "pattern": "\\b\\w{50,}\\b",
                    "replacement": ""
                    },
                "reddit_handle_replace": {
                    "type": "pattern_replace",
                    "pattern": "/u/[A-Za-z0-9_-]+",
                    "replacement": "__reddit_handle__"
                    },
                "twitter_handle_replace": {
                    "type": "pattern_replace",
                    "pattern": "/(^|[^@\\w])@(\\w{1,15})\\b/",
                    "replacement": "__twitter_handle__"
                    }
                },
            "filter": {
                "crypto_synonym": {
                    "type": "synonym_graph",
                    "synonyms": [
                        "hodl, hold, \ud83d\udc8e\ud83d\ude4c, \ud83d\udc8e => hold",
                        "halving, halvening => halving",
                        "fomo, fear of missing out",
                        "fud, fear uncertainty doubt => fear uncertainty doubt",
                        "mooning, spike, spiking => spike",
                        "ripple, xrp => ripple",
                        "litecoin, ltc => litecoin",
                        "tether, teth, usdt => tether",
                        "btc, xbt, bitcoin, sats => bitcoin",
                        "eth, ether, ethereum => ethereum",
                        "cryptocurrency, cryptocurrencies, crypto => crypto",
                        "tx, transaction => transaction",
                        "usd, us dollars, us dollar, dollar, dollars => usd",
                        "lightning network, ln => lightning network",
                        "rekt, wrecked => wrecked"
                        ]
                    },
                "english_stop": {
                    "stopwords": "_english_",
                    "type": "stop"
                    }
                }
            }
        },
    "mappings": {
        "properties": {
            "id": {"type": "keyword"},
            "subreddit": {"type": "keyword"},
            "create_datetime": {"type": "date"},
            "author": {"type": "keyword"},
            "full_text": {
                "type": "text",
                "analyzer": "reddit_index_analyzer"
                },
            "type": {"type": "keyword"},
            "parent_id": {"type": "keyword"},
        }
    }
}
