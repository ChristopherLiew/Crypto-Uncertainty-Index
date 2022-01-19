"""
Helper class to insert and query documents from Elasticsearch 
"""


import pandas as pd
from typing import (
    Any,
    Callable,
    List,
    Dict,
    Optional,
    Union,
    Generator
)
from dataclasses import (
    dataclass,
    is_dataclass
)
from elasticsearch import Elasticsearch
from ..utils.logger import log
# from elasticsearch_dsl import Search  # Use for easy search


class ESManager:
    def __init__(
        self, host: str = "localhost", port: int = 9200, timeout: int = 180
    ) -> None:

        self.es_client = Elasticsearch(
            [{"host": host, "port": port}],
            timeout=timeout,
            max_retries=3,
            retry_on_timeout=True,
        )

    def status(self) -> None:
        log.info(str(self.es_client.ping()))

    @staticmethod
    def es_doc_generator(self,
                         data: Union[pd.DataFrame, List[dataclass]],
                         index: str,
                         auto_id: bool = True,
                         id_field: Optional[str] = None,
                         doc_processing_func: Optional[Callable] = None
                         ) -> Generator:

        if isinstance(data, pd.DataFrame):
            data = data.to_dict(orient='records')

        for rec in data:
            doc = {
                "_index": index,
                "_type": "_doc",
                # NOTE: Processing func must handle dataclasses
                # or dict and return a dict
                "_source": rec if not doc_processing_func
                else doc_processing_func(rec)
            }
            if auto_id:
                yield doc  # Let ES auto-generate an id for each doc
            elif not auto_id and id_field:
                doc['_id'] = rec[id_field]
                yield doc  # Provide your own id for each doc
            elif not auto_id and not id_field:
                log.exception("Please provide the id field to uniquely identify a doc")
                break

    def create_index(
        self,
        index: str,
        mapping: Dict[str, str],
        body: List[Any] = None,
        settings: Dict[str, str] = None,
    ) -> None:

        request = {}
        request["settings"] = (
            {"number_of_shards": 5, "number_of_replicas": 1}
            if not settings
            else settings
        )
        request["mappings"] = mapping
        data_size = 0 if not body else len(body)

        log.info(
            f"""
              Creating Index with name: {index} |
              mapping: {mapping} |
              data of size: {data_size}"""
        )
        log.info(f"Index Settings: {settings}")

        resp = self.es_client.create(index=index, body=request)
        log.info(resp)

    def get_index(self, index: str) -> bool:
        return (
            self.es_client
            .indices
            .exists(index=index)
        )

    def bulk_insert_data(self,
                         index: str,
                         data: Union[Generator, List[Dict[Any]]]
                         ) -> None:
        resp = self.es_client.bulk(index=index, body=data)
        log.info(resp)

    def delete_index(self, index: str) -> None:
        resp = self.es_client.delete(index=index, ignore=404)
        log.info(resp)

    def run_match_query(
        self, index: str, query: Dict[str, str], output_type: str = "pandas"
    ) -> Union[List, pd.DataFrame]:
        raw = self.es_client(index=index, body=query)
        res = [doc["hits"]["hits"] for doc in raw]
        return pd.DataFrame(res) if output_type == "panads" else res
