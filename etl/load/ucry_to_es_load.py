import pandas as pd
from es.manager import ESManager
from etl.schema.es_mappings import (
    LUCEY_UNCERTAINTY_INDEX_NAME,
    ucry_index_mapping
)
from utils import timer
from utils.logger import log

static_es_conn = ESManager()
DATE_FMT = "%Y-%m-%d"


@timer
def insert_ucry_to_es(
    data: pd.DataFrame, index: str = LUCEY_UNCERTAINTY_INDEX_NAME
) -> None:
    log.info("Inserting data to ES")
    if not static_es_conn.index_is_exist(index):
        log.info(f"{index} not yet created ... creating index: {index}")
        (
            static_es_conn
            .create_index(index=index, mapping=ucry_index_mapping)
        )
    log.info("Generating ES compatible documents")
    lucey_ucry_docs = ESManager().es_doc_generator(
        data=data,
        index=index,
        auto_id=True,
        doc_processing_func=None,
    )
    print(next(lucey_ucry_docs))
    log.info("Documents generated. Inserting documents into ES.")
    static_es_conn.bulk_insert_data(index=index, data=lucey_ucry_docs)
    log.info("Insertion complete!")
