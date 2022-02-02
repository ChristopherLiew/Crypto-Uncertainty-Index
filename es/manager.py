"""
Helper class to insert and query documents from Elasticsearch.
"""


import pandas as pd
from pprint import pprint
from typing import Any, Callable, List, Dict, Optional, Union, Generator
from dataclasses import dataclass
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from elasticsearch.exceptions import RequestError
from utils.logger import log
from config.es_cfg import (
    DEFAULT_HOST,
    DEFAULT_PORT,
    DEFAULT_INDEX_SETTINGS
)

# from elasticsearch_dsl import Search Use for easy search


class ESManager:
    def __init__(
        self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, timeout: int = 180
    ) -> None:

        self.es_client = Elasticsearch(
            [{"host": host, "port": port}],
            timeout=timeout,
            max_retries=3,
            retry_on_timeout=True,
        )

    def get_status(self) -> bool:
        return self.es_client.ping()

    @staticmethod
    def es_doc_generator(
        data: Union[pd.DataFrame, List[dataclass]],
        index: str,
        auto_id: bool = True,
        id_field: Optional[str] = None,
        doc_processing_func: Optional[Callable] = None,
    ) -> Generator:

        if isinstance(data, pd.DataFrame):
            data = data.to_dict(orient="records")

        for rec in data:
            doc = {
                "_index": index,
                "_type": "_doc",
                # NOTE: Processing func must handle dataclasses
                # or dict and return a dict
                "_source": rec if not doc_processing_func else doc_processing_func(rec),
            }
            if auto_id:
                yield doc  # Let ES auto-generate an id for each doc
            elif not auto_id and id_field:
                doc["_id"] = rec[id_field]
                yield doc  # Provide your own id for each doc
            elif not auto_id and not id_field:
                log.exception("Please provide the unique id field")
                break

    def create_index(
        self,
        index: str,
        mapping: Dict[str, str],
        body: List[Any] = None,
        settings: Dict[str, str] = None,
        separate_settings: bool = True
    ) -> None:

        if separate_settings:
            mapping["settings"] = DEFAULT_INDEX_SETTINGS if not settings else settings

        data_size = 0 if not body else len(body)

        log.info(
            f"""
              Creating Index with name: {index} |
              mapping: {mapping} |
              data of size: {data_size}"""
        )
        log.info(
            f"""
                 Index Settings:
                 {settings if settings else DEFAULT_INDEX_SETTINGS}
                 """
        )

        try:
            resp = self.es_client.indices.create(index=index, body=mapping)
            log.info(resp)
        except RequestError as e:
            log.exception(e)

    def index_is_exist(self, index: str) -> bool:
        return self.es_client.indices.exists(index=index)

    def bulk_insert_data(
        self, index: str, data: Union[Generator, List[Dict[str, Any]]]
    ) -> None:
        resp = bulk(self.es_client, index=index, actions=data)
        log.info(resp)

    def delete_index(self, index: str) -> None:
        resp = self.es_client.indices.delete(index=index, ignore=404)
        log.info(resp)

    def reindex(self, source_index: str, dest_index: str, timeout: int = 10000) -> None:
        assert self.index_is_exist(source_index),\
            f"Source Index: {source_index} does not exist!"
        assert self.index_is_exist(dest_index),\
            f"Destination Index: {dest_index} does not exist!"

        reindex_query = {
            "source": {
                "index": source_index
                },
            "dest": {
                "index": dest_index
                }
            }
        self.es_client.reindex(reindex_query,
                               wait_for_completion=True,
                               request_timeout=timeout,
                               slices='auto',
                               refresh=True)

    def add_alias(self, index: List[str], alias: str) -> None:
        self.es_client.indices.put_alias(
            index=index,
            name=alias
        )

    def remove_alias(self, index: str, alias: str) -> None:
        self.es_client.indices.delete_alias(
            index=index,
            name=alias
        )

    def get_aliases(self, name: Optional[List[str]] = None) -> None:
        pprint(self.es_client.cat.aliases(name=name))

    def run_match_query(
        self, index: str, query: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        res = self.es_client.search(index=index, body=query)["hits"]["hits"]
        return res
