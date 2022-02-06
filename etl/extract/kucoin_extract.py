"""
Extract Crypto Related Data from KuCoin API.
See: https://docs.kucoin.com/#get-symbols-list

Rate Limit:
For each query, the system would return at most **1500** pieces of data.
To obtain more data, please page the data by time.

Historical Data Limit:
KuCoin historical data only goes up to 5 years back. If ALL data is required
please download manually from CMC or CoinDesk.
"""

import toml
import requests
from tqdm import tqdm
from datetime import datetime
from pathlib import Path
from typing import List, Union
from etl.schema.kucoin_classes import KuCoinCandle
from utils.logger import log
from utils.serializer import write_to_pkl


# Config
DATE_FMT = "%Y-%m-%d"
ku_coin_config = toml.load(Path() / "config" / "etl_config.toml")["kucoin"]
BASE_URL = ku_coin_config["base_url"]
DEFAULT_FREQUENCY = ku_coin_config["default_frequency"]
CRYPTO_PRICE_SAVE_DIR = Path(ku_coin_config["save_dir"])
START_DATE, END_DATE = (
    datetime
    .strptime(ku_coin_config["start_date"], DATE_FMT),
    datetime
    .strptime(ku_coin_config["end_date"], DATE_FMT)
)


def extract_kucoin_price_data(coin_pair: str,
                              start_date: datetime = START_DATE,
                              end_date: datetime = END_DATE,
                              frequency: str = DEFAULT_FREQUENCY,
                              save_dir: Union[str, Path] = CRYPTO_PRICE_SAVE_DIR
                              ) -> List[KuCoinCandle]:

    start_date = int(start_date.timestamp())
    end_date = int(end_date.timestamp())
    curr_date = end_date
    all_data = []
    log.info(f"Pulling {coin_pair} from KuCoin API for range:\
        {start_date} to {end_date}")

    while curr_date > start_date:
        query = (
            BASE_URL
            + f"/api/v1/market/candles?type={frequency}&symbol={coin_pair}\
                &startAt={start_date}&endAt={curr_date}"
        )
        body = requests.get(query).json()
        data = body['data']
        if len(data) > 0:
            curr_date = int(data[-1][0])
            all_data.extend(data)
        else:
            log.info("Data pulling complete!")
            break

    # Convert and validate data
    log.info("Converting and validating raw data with pydantic")
    all_data_fmt = [KuCoinCandle(*obs) for obs in tqdm(all_data)]
    log.info(f"Writing to pkl at: {save_dir}")
    write_to_pkl(save_dir, all_data_fmt)

    return all_data_fmt
