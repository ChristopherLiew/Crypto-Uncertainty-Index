POST /reddit-crypto-custom/_count
{
        "query": {
            "bool": {
                "must": [
                    {"terms": 
                      {"full_text": ["bitcoin", "ethereum", "ripple", "litecoin","tether", "cryptocurrency", "cryptocurrencies"]}
                    },
                    {"wildcard":
                      {"full_text": "pric*"}
                    },
                    {"wildcard": 
                      {"full_text": "uncertain*"}
                    },
                    {"range": 
                      {"create_datetime": {
                        "gte": "2014-01-01",
                        "lte": "2021-12-31"
                      }
                    }
                  }
                ]
            }
        }
    }
    
PUT /reddit-crypto-custom/_settings


POST /reddit-crypto-custom/_analyze
{
  "analyzer": "standard",
  "text": "That comment isnt really about Eth or crypto or blockchain, its true of any financial investment. I’m 100% confident that if the creator of Ethereum tragically dies or otherwise disappears, Ethereum prices will go down, even if only temporarily. The same would happen to Amazon if Bezos disappears, to FB if Zuck disappears, etc etc. it will create market uncertainty"
}

PUT /test-custom-analyzer?pretty
{
  "settings": {
    "analysis": {
    "analyzer": {
        "reddit_index_analyzer": {
            "char_filter": [
                "html_strip",
                "emoticons",
                "crypto_lex",
                "general_en_contractions",
                "reddit_handle_replace",
                "twitter_handle_replace",
                "lengthy_char_replace"
            ],
            "filter": [
                "lowercase",
                "asciifolding",
                "english_stop",
                "kstem"
            ],
            "tokenizer": "standard",
            "type": "custom"
        }
    },
    "char_filter": {
        "emoticons": {
            "mappings": [
                ":) => happy",
                ":( => sad",
                "\ud83d\udc0b => whale",
                ":/ => 'Skeptical, annoyed, undecided, uneasy or hesitant'",
                "%) => 'Drunk or confused'"
            ],
            "type": "mapping"
        },
        "general_en_contractions": {
            "mappings": [
                "ain't => am not / are not / is not / has not / have not",
                "aren't => are not / am not",
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
                "he'd => he had / he would",
                "he'd've => he would have",
                "he'll => he shall / he will",
                "he'll've => he shall have / he will have",
                "he's => he has / he is",
                "how'd => how did",
                "how'd'y => how do you",
                "how'll => how will",
                "how's => how has / how is / how does",
                "I'd => I had / I would",
                "I'd've => I would have",
                "I'll => I shall / I will",
                "I'll've => I shall have / I will have",
                "I'm => I am",
                "I've => I have",
                "isn't => is not",
                "it'd => it had / it would",
                "it'd've => it would have",
                "it'll => it shall / it will",
                "it'll've => it shall have / it will have",
                "it's => it has / it is",
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
                "she'd => she had / she would",
                "she'd've => she would have",
                "she'll => she shall / she will",
                "she'll've => she shall have / she will have",
                "she's => she has / she is",
                "should've => should have",
                "shouldn't => should not",
                "shouldn't've => should not have",
                "so've => so have",
                "so's => so as / so is",
                "that'd => that would / that had",
                "that'd've => that would have",
                "that's => that has / that is",
                "there'd => there had / there would",
                "there'd've => there would have",
                "there's => there has / there is",
                "they'd => they had / they would",
                "they'd've => they would have",
                "they'll => they shall / they will",
                "they'll've => they shall have / they will have",
                "they're => they are",
                "they've => they have",
                "to've => to have",
                "wasn't => was not",
                "we'd => we had / we would",
                "we'd've => we would have",
                "we'll => we will",
                "we'll've => we will have",
                "we're => we are",
                "we've => we have",
                "weren't => were not",
                "what'll => what shall / what will",
                "what'll've => what shall have / what will have",
                "what're => what are",
                "what's => what has / what is",
                "what've => what have",
                "when's => when has / when is",
                "when've => when have",
                "where'd => where did",
                "where's => where has / where is",
                "where've => where have",
                "who'll => who shall / who will",
                "who'll've => who shall have / who will have",
                "who's => who has / who is",
                "who've => who have",
                "why's => why has / why is",
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
                "you'd => you had / you would",
                "you'd've => you would have",
                "you'll => you shall / you will",
                "you'll've => you shall have / you will have",
                "you're => you are",
                "you've => you hav"
            ],
            "type": "mapping"
        },
        "lengthy_char_replace": {
            "pattern": "\\b\\w{50,}\\b",
            "replacement": "",
            "type": "pattern_replace"
        },
        "reddit_handle_replace": {
            "pattern": "/u/[A-Za-z0-9_-]+",
            "replacement": "__reddit_handle__",
            "type": "pattern_replace"
        },
        "twitter_handle_replace": {
            "pattern": "/(^|[^@\\w])@(\\w{1,15})\\b/",
            "replacement": "__twitter_handle__",
            "type": "pattern_replace"
        }
    },
    "filter": {
        "crypto_synonym": {
            "synonyms": [
                "hodl, hold, \ud83d\udc8e\ud83d\ude4c, \ud83d\udc8e => hold",
                "halving, halvening => halving",
                "fomo, fear of missing out => fear_of_missing_out",
                "fud, fear uncertainty doubt => fear_uncertainty_doubt",
                "btc, xbt, bitcoin => bitcoin",
                "eth, ether, ethereum => ethereum",
                "tx, transaction => transaction",
                "usd, us dollars, us dollar, dollar, dollars, $ => usd",
                "lightning network, ln => lightning network"
            ],
            "type": "synonym"
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
      "my_text": {
        "type": "text",
        "analyzer": "std_folded" 
      }
    }
  }
}


GET /my-index-000001/_analyze?pretty
{
  "analyzer": "std_folded", 
  "text":     "Is this déjà vu?"
}


GET /my-index-000001/_analyze?pretty
{
  "field": "my_text", 
  "text":  "Is this déjà vu?"
}