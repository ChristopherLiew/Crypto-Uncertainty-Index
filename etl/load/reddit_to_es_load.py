from typing import (
    List,
    Dict,
    Any,
    Union,
)
from etl.schema.es_mappings import reddit_crypto_mapping, REDDIT_CRYPTO_INDEX_NAME
from snscrape.modules.reddit import (
    Submission,
    Comment
)
from es.manager import ESManager
from utils.logger import log
from utils import timer

try:
    es_static_client = ESManager()
except Exception as e:
    log.exception(f"Cannot connect to ES instance: {e}")


sns_reddit_op_type = List[Union[Submission, Comment]]


# Use these functions to tidy up and generate the docs
def process_reddit_comments_and_submissions(
    reddit_document: Union[Submission, Comment]
) -> Dict[str, Any]:
    base_doc = {
        "id": reddit_document.id,
        "subreddit": reddit_document.subreddit,
        "create_datetime": reddit_document.created,
        "author": reddit_document.author,
    }
    if isinstance(reddit_document, Submission):
        base_doc["full_text"] = f"{reddit_document.title} {reddit_document.selftext}"
        base_doc["type"] = "submission"
        base_doc["parent_id"] = None
    else:
        base_doc["full_text"] = reddit_document.body
        base_doc["type"] = "comment"
        base_doc["parent_id"] = reddit_document.parentId
    return base_doc


@timer
def insert_reddit_to_es(
    data: sns_reddit_op_type, index: str = REDDIT_CRYPTO_INDEX_NAME
) -> None:

    log.info("Inserting data to ES")
    if not es_static_client.index_is_exist(index):
        log.info(f"{index} not yet created ... creating index: {index}")
        (es_static_client.create_index(index=index, mapping=reddit_crypto_mapping))

    log.info("Generating ES compatible documents")
    reddit_crypto_gen = ESManager().es_doc_generator(
        data=data,
        index=index,
        auto_id=True,
        doc_processing_func=process_reddit_comments_and_submissions,
    )

    log.info("Documents generated. Inserting documents into ES.")
    es_static_client.bulk_insert_data(index=index, data=reddit_crypto_gen)
    log.info("Insertion complete!")
