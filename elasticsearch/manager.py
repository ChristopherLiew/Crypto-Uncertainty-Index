"""
Helper class to insert and query documents from Elasticsearch 
"""

import pandas as pd
from tqdm import tqdm
from typing import (
    Any,
    List,
    Dict,
    Union
)
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search # Use for easy search


class ESManager:
    def __init__(self,
                 host: str = 'localhost',
                 port: int = 9200,
                 timeout: int = 180) -> None:

        self.es_client = Elasticsearch(
            [{'host': host, 'port': port}],
            timeout=timeout,
            max_retries=3,
            retry_on_timeout=True)

    def status(self) -> None:
        print(str(self.es_client.ping()))

    def pd_to_es(self, pd_df: pd.DataFrame) -> Dict[Any, Any]:
        pass

    def create_index(self,
                     index: str,
                     mapping: Dict[str, str],
                     body: List[Any] = None,
                     settings: Dict[str, str] = None) -> None:

        request = {}
        request['settings'] = {
            "number_of_shards": 5,
            "number_of_replicas": 1
            } if not settings else settings
        request['mappings'] = mapping
        data_size = 0 if not body else len(body)

        print(f"Index Settings: {settings}")
        print(f"""
              Creating Index with name: {index} |
              mapping: {mapping} |
              data of size: {data_size}""")

        resp = self.es_client.create(index=index, body=request)
        print(resp)

    def bulk_insert_data(self, index: str, data: List[Dict[Any]]) -> None:
        resp = self.es_client.bulk(index=index, body=data)
        print(resp)

    def delete_index(self, index: str) -> None:
        resp = self.es_client.delete(index=index, ignore=404)
        print(resp)

    def run_match_query(self,
                        index: str,
                        query: Dict[str, str],
                        output_type: str = 'pandas'
                        ) -> Union[List, pd.DataFrame]:
        raw = self.es_client(index=index, body=query)
        res = [doc['hits']['hits'] for doc in raw]
        return pd.DataFrame(res) if output_type == 'panads' else res
