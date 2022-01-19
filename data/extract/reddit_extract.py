"""
Extraction functions to pull historical submissions and comments data
from Reddit.
"""


# TO DO:
# 1) Test functionality with small sample of 7 days of data from
# 1 subreddit capped at 10,000 docs per day + ES manager functionality
# 2) Start pulling data and update Data Dictionary

from pprint import pprint
from tqdm import tqdm
from typing import (
    List,
    Dict,
    Any,
    Union,
    Optional
)
from datetime import datetime
# from psaw import PushshiftAPI
from snscrape.modules.reddit import (
    RedditSubredditScraper,
    Submission,
    Comment
)
from data.schema.es_mappings import (
    reddit_crypto_mapping,
    REDDIT_CRYPTO_INDEX_NAME
)
from es.manager import ESManager
from utils.logger import log

# Set Up
# push_api = PushshiftAPI()
es_static_client = ESManager()

# To see schema of Subreddit dataclasses:
# pprint(Submission.__annotations__)
# pprint(Comment.__annotations__)
sns_reddit_op_type = Dict[str, List[Union[Submission, Comment]]]

# Config
DATE_FMT = "%Y-%m-%d"


# Use these functions to tidy up and generate the docs
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


def insert_reddit_to_es(
    data: sns_reddit_op_type
) -> None:
    try:
        es_conn = ESManager()
    except Exception:
        log.exception("Cannot connect to ES instance")

    for sr_name, data in data.items():
        log.info(f"Inserting data from {sr_name} to ES")
        if not es_conn.index_is_exist(REDDIT_CRYPTO_INDEX_NAME):
            log.info(f"{REDDIT_CRYPTO_INDEX_NAME} not yet created")
            es_conn.create_index(index=REDDIT_CRYPTO_INDEX_NAME,
                                 mapping=reddit_crypto_mapping)
        log.info("Generating ES compatible documents")
        reddit_crypto_gen = (
            ESManager()
            .es_doc_generator(data=data,
                              index=REDDIT_CRYPTO_INDEX_NAME,
                              auto_id=True,
                              doc_processing_func=process_reddit_comments_and_submissions)
            )
        log.info("Documents generated. Inserting documents into ES.")
        es_conn.bulk_insert_data(index=REDDIT_CRYPTO_INDEX_NAME,
                                 data=reddit_crypto_gen)
        log.info("Insertion complete!")


def get_all_crypto_subreddit_data(
    subreddits: List[str],
    start_date: Union[str, datetime],
    end_date: Union[str, datetime],
    max_results_per_subreddit: Optional[int] = 1000,  # If None get ALL data
) -> sns_reddit_op_type:
    results = {name: None for name in subreddits}
    if isinstance(start_date, str) or isinstance(end_date, str):
        start_date = datetime.strptime(start_date, DATE_FMT)
        end_date = datetime.strptime(end_date, DATE_FMT)
    for i in tqdm(range(len(subreddits))):
        curr_res = list()
        sr_name = subreddits[i]
        log.info(
            msg=f"""Pulling data from subreddit={sr_name}
                 for dates between {str(start_date)} and {str(end_date)}"""
        )
        scraper = RedditSubredditScraper(sr_name,
                                         before=end_date,
                                         after=start_date)

        for idx, content in enumerate(scraper.get_items()):
            if max_results_per_subreddit and idx > max_results_per_subreddit:
                break
            curr_res.append(content)
        log.info(msg=f"Successfully pulled data from subreddit={sr_name}")
        results[sr_name] = curr_res
    log.info(msg="All subreddit sucessfully pulled")
    return results
