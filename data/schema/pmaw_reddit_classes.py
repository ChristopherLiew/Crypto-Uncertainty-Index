"""
Dataclasses for PMAW mappings. Classes are to map PMAW output
results to SNSCRAPE dataclass schema for consistent data abstraction.

NOTE: Mappings may not be consistent with SNSCRAPE entirely due to
differing fields returned by PMAW vis a vis SNSCRAPE.
"""

from dataclasses import (
    dataclass,
    asdict
)
from datetime import datetime
from typing import Optional
from snscrape.modules.reddit import (
    Comment,
    Submission
)


@dataclass
class SubmissionPMAW:
    created_utc: int
    id: str
    title: str
    subreddit: str
    url: Optional[str] = None
    author: Optional[str] = None
    permalink: Optional[str] = None
    selftext: Optional[str] = None

    def to_reddit_standard(self) -> Submission:
        doc = asdict(self)
        doc['created'] = datetime.fromtimestamp(self.created_utc)
        doc['link'] = self.permalink
        del doc['created_utc']
        del doc['permalink']
        return Submission(**doc)


@dataclass
class CommentPMAW:
    created_utc: int
    id: str
    body: str
    subreddit: str
    author: Optional[str] = None
    parent_id: Optional[str] = None
    permalink: Optional[str] = None

    def to_reddit_standard(self) -> Comment:
        doc = asdict(self)
        doc['created'] = datetime.fromtimestamp(self.created_utc)
        doc['url'] = self.permalink
        doc['parentId'] = self.parent_id
        del doc['created_utc']
        del doc['permalink']
        del doc['parent_id']
        return Comment(**doc)
