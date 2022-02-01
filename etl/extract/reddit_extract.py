"""
Extraction functions to pull historical submissions and comments data
from Reddit.
"""

from typing import (
    List,
    Dict,
    Any,
    Union,
    Optional
)
from datetime import datetime
from pmaw import PushshiftAPI
from requests.exceptions import ChunkedEncodingError
from snscrape.modules.reddit import (
    RedditSubredditScraper,
    Submission,
    Comment
)
from etl.schema.pmaw_reddit_classes import (
    SubmissionPMAW,
    CommentPMAW
)
from etl.schema.es_mappings import (
    reddit_crypto_mapping,
    REDDIT_CRYPTO_INDEX_NAME
)
from dacite import from_dict
from es.manager import ESManager
from utils import timer
from utils.logger import log

# Set Up
# from psaw import PushshiftAPI
# push_api = PushshiftAPI()
# Connect to ES
try:
    es_static_client = ESManager()
except Exception as e:
    log.exception(f"Cannot connect to ES instance: {e}")

try:
    api = PushshiftAPI()
except Exception as e:
    log.exception(f"Unable to connect to PushshiftAPI: {e}")

# To see schema of Subreddit dataclasses:
# pprint(Submission.__annotations__)
# pprint(Comment.__annotations__)
sns_reddit_op_type = List[Union[Submission, Comment]]

# Config
DATE_FMT = "%Y-%m-%d"


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
        (
            es_static_client
            .create_index(index=index, mapping=reddit_crypto_mapping)
        )

    log.info("Generating ES compatible documents")
    reddit_crypto_gen = ESManager().es_doc_generator(
        data=data,
        index=index,
        auto_id=True,
        doc_processing_func=process_reddit_comments_and_submissions,
    )

    log.info("Documents generated. Inserting documents into ES.")
    (es_static_client.bulk_insert_data(index=index, data=reddit_crypto_gen))
    log.info("Insertion complete!")


@timer
def extract_subreddit_data(
    subreddit: str,
    start_date: Union[str, datetime],
    end_date: Union[str, datetime],
    limit: Optional[int] = 9999999,  # If None get ALL data
    scraper: str = "pmaw",
    **kwargs,
) -> List[Union[Comment, Submission]]:
    if isinstance(start_date, str) or isinstance(end_date, str):
        start_date = datetime.strptime(start_date, DATE_FMT)
        end_date = datetime.strptime(end_date, DATE_FMT)
    results = []
    log.info(
        msg=f"""Pulling data from subreddit={subreddit}
                for dates between {str(start_date)} and {str(end_date)}"""
    )
    if scraper.lower() == "snscrape":
        sc = RedditSubredditScraper(subreddit,
                                    before=end_date,
                                    after=start_date)

        for idx, content in enumerate(sc.get_items()):
            if limit and idx > limit:
                break
            results.append(content)
    elif scraper.lower() == "pmaw":
        start_ts = int(start_date.timestamp())
        end_ts = int(end_date.timestamp())
        try:
            comment_res = api.search_comments(
                subreddit=subreddit,
                before=end_ts,
                after=start_ts,
                limit=limit,
                mem_safe=kwargs["mem_safe"],
                safe_exit=kwargs["safe_exit"],
            )
            comment_res_standardised = [
                from_dict(data_class=CommentPMAW, data=comment)
                .to_reddit_standard()
                for comment in (comment_res)
            ]
            results.extend(comment_res_standardised)
        except ChunkedEncodingError:
            (
                log
                .exception("PushshiftAPI (Comments) dropped due to ChunkedEncodingError")
            )
        try:
            submissions_res = api.search_submissions(
                subreddit=subreddit,
                before=end_ts,
                after=start_ts,
                limit=limit,
                mem_safe=kwargs["mem_safe"],
                safe_exit=kwargs["mem_safe"],
            )
            submissions_res_standardised = [
                from_dict(data_class=SubmissionPMAW, data=sub)
                .to_reddit_standard()
                for sub in (submissions_res)
            ]
            results.extend(submissions_res_standardised)
        except ChunkedEncodingError:
            log.exception(
                "PushshiftAPI (Submissions) dropped due to ChunkedEncodingError"
            )

    else:
        raise ValueError("Please select a valid scraper: pmaw or snscrape")
    log.info(msg=f"Successfully pulled data from subreddit: {subreddit}")
    return results
