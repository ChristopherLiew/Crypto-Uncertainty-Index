"""
Reddit Crypto Data Extraction Configs
"""

from datetime import datetime


CRYPTO_SUBREDDITS = [
    # Ethereum
    "ethereum",
    "ethtrader",
    "EtherMining",
    # Bitcoin
    "Bitcoin",
    "BitcoinMarkets",
    "btc",
    # Others
    "CryptoCurrency",
    "CryptoCurrencyTrading",
]

CRYPTO_REDDIT_DATE_RANGE = {
    "start_date": datetime.strptime("2014-01-01", "%Y-%m-%d"),
    "end_date": datetime.strptime("2021-12-31", "%Y-%m-%d"),
}

REDDIT_DATA_SAVE_DIR = "/Users/christopherliew/Desktop/Y4S1/HT/crypto_uncertainty_index/data/raw_data_dump/reddit"
