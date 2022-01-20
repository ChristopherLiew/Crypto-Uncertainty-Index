"""
Extraction functions to pull historical submissions and comments data
from Reddit.
"""

# TO DO:
# 1) Test functionality with small sample of 7 days of data from
# 1 subreddit capped at 10,000 docs per day + ES manager functionality
# 2) Start pulling data and update Data Dictionary

from tqdm import tqdm
from typing import (
    List,
    Dict,
    Any,
    Union,
    Optional
)
from datetime import datetime
from pmaw import PushshiftAPI
from snscrape.modules.reddit import (
    RedditSubredditScraper,
    Submission,
    Comment
)
from data.schema.es_mappings import (
    reddit_crypto_mapping,
    REDDIT_CRYPTO_INDEX_NAME
)
from data.schema.pmaw_reddit_classes import (
    SubmissionPMAW,
    CommentPMAW
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
sns_reddit_op_type = Dict[str, List[Union[Submission, Comment]]]

# Config
DATE_FMT = "%Y-%m-%d"


# Use these functions to tidy up and generate the docs
@timer
def process_reddit_comments_and_submissions(
    reddit_document: Union[Submission, Comment]
) -> Dict[str, Any]:
    base_doc = {
            'id': reddit_document.id,
            'subreddit': reddit_document.subreddit,
            'create_datetime': reddit_document.created,
            'author': reddit_document.author
        }
    if isinstance(reddit_document, Submission):
        base_doc['full_text'] = f'{reddit_document.title} {reddit_document.selftext}'
        base_doc['type'] = 'submission'
        base_doc['parent_id'] = None
    else:
        base_doc['full_text'] = reddit_document.body
        base_doc['type'] = 'comment'
        base_doc['parent_id'] = reddit_document.parentId
    return base_doc


@timer
def insert_reddit_to_es(
    data: sns_reddit_op_type
) -> None:

    for sr_name, data in data.items():

        log.info(f"Inserting data from {sr_name} to ES")
        if not es_static_client.index_is_exist(REDDIT_CRYPTO_INDEX_NAME):
            log.info(f"{REDDIT_CRYPTO_INDEX_NAME} not yet created")
            (
                es_static_client
                .create_index(index=REDDIT_CRYPTO_INDEX_NAME,
                              mapping=reddit_crypto_mapping)
            )

        log.info("Generating ES compatible documents")
        reddit_crypto_gen = (
            ESManager()
            .es_doc_generator(
                data=data,
                index=REDDIT_CRYPTO_INDEX_NAME,
                auto_id=True,
                doc_processing_func=process_reddit_comments_and_submissions)
            )

        log.info("Documents generated. Inserting documents into ES.")
        (
            es_static_client
            .bulk_insert_data(index=REDDIT_CRYPTO_INDEX_NAME,
                              data=reddit_crypto_gen)
        )
        log.info("Insertion complete!")


@timer
def get_all_crypto_subreddit_data(
    subreddit: str,
    start_date: Union[str, datetime],
    end_date: Union[str, datetime],
    limit: Optional[int] = 9999999,  # If None get ALL data
    scraper: str = "pmaw"
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
        comment_res = api.search_comments(
            subreddit=subreddit,
            before=end_ts,
            after=start_ts,
            limit=limit
        )
        submissions_res = api.search_submissions(
            subreddit=subreddit,
            before=end_ts,
            after=start_ts,
            limit=limit
        )
        comment_res_standardised = [
            from_dict(data_class=CommentPMAW, data=comment)
            .to_reddit_standard()
            for comment in tqdm(comment_res)
        ]
        submissions_res_standardised = [
            from_dict(data_class=SubmissionPMAW, data=sub)
            .to_reddit_standard()
            for sub in tqdm(submissions_res)
        ]
        results.extend(comment_res_standardised)
        results.extend(submissions_res_standardised)
    else:
        raise ValueError("Please select a valid scraper: pmaw or snscrape")
    log.info(msg=f"Successfully pulled data from subreddit: {subreddit}")

    log.info(msg="All subreddit sucessfully pulled")
    return results
