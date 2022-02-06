"""
Extraction functions to pull historical submissions and comments data
from Reddit.
"""

from typing import (
    List,
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

from dacite import from_dict
from es.manager import ESManager
from utils import timer
from utils.logger import log

try:
    es_static_client = ESManager()
except Exception as e:
    log.exception(f"Cannot connect to ES instance: {e}")

try:
    api = PushshiftAPI()
except Exception as e:
    log.exception(f"Unable to connect to PushshiftAPI: {e}")


sns_reddit_op_type = List[Union[Submission, Comment]]

# Config
DATE_FMT = "%Y-%m-%d"


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
                .to_sns_scrape_standard()
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
                .to_sns_scrape_standard()
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
