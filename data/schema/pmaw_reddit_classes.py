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
from pprint import pprint


pprint(Submission.__annotations__)
pprint(Comment.__annotations__)


@dataclass
class SubmissionPMAW:
    author: Optional[str]
    created_utc: int
    id: str
    permalink: Optional[str]
    selftext: Optional[str]
    subreddit: Optional[str]  # E.g. submission 617p51
    title: str
    url: str

    def to_reddit_standard(self) -> Submission:
        doc = asdict(self)
        doc['created'] = datetime.fromtimestamp(self.created_utc)
        doc['link'] = self.permalink
        del doc['created_utc']
        del doc['permalink']
        return Submission(**doc)


@dataclass
class CommentPMAW:
    author: Optional[str]
    body: str
    created_utc: int
    id: str
    parent_id: Optional[str]
    subreddit: Optional[str]
    permalink: str

    def to_reddit_standard(self) -> Comment:
        doc = asdict(self)
        doc['created'] = datetime.fromtimestamp(self.created_utc)
        doc['url'] = self.permalink
        doc['parentId'] = self.parent_id
        del doc['created_utc']
        del doc['permalink']
        del doc['parent_id']
        return Comment(**doc)
