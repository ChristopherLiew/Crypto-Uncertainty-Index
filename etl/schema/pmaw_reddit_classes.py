"""
Dataclasses for PMAW mappings. Classes are to map PMAW output
results to SNSCRAPE dataclass schema for consistent data abstraction.

NOTE: Mappings may not be consistent with SNSCRAPE entirely due to
differing pydantic.Field(s returned by PMAW vis a vis SNSCRAPE.
"""


import pydantic
from dataclasses import asdict
from datetime import datetime
from typing import Optional
from snscrape.modules.reddit import (
    Comment,
    Submission
)


@pydantic.dataclasses.dataclass
class SubmissionPMAW:
    created_utc: int
    id: str
    title: str
    subreddit: str
    url: Optional[pydantic.AnyUrl] = pydantic.Field(None, description="URL to reddit submission")
    author: Optional[str] = pydantic.Field(None, description="Author of reddit submission")
    permalink: Optional[str] = pydantic.Field(None, description="Link reddit submission")
    selftext: Optional[str] = pydantic.Field(None, description="Body of reddit submission")

    def __post_init__(self) -> None:
        self.created_utc = datetime.fromtimestamp(self.created_utc)

    def to_sns_scrape_standard(self) -> Submission:
        doc = asdict(self)
        doc["created"] = self.created_utc
        doc["link"] = self.permalink
        del doc["created_utc"]
        del doc["permalink"]
        return Submission(**doc)


@pydantic.dataclasses.dataclass
class CommentPMAW:
    created_utc: int
    id: str
    body: str
    subreddit: str
    author: Optional[str] = pydantic.Field(None, description="Author of reddit comment")
    parent_id: Optional[str] = pydantic.Field(None, description="Parent id of reddit comment")
    permalink: Optional[str] = pydantic.Field(None, description="Link reddit comment")

    def __post_init__(self) -> None:
        self.created_utc = datetime.fromtimestamp(self.created_utc)

    def to_sns_scrape_standard(self) -> Comment:
        doc = asdict(self)
        doc["created"] = self.created_utc
        doc["url"] = self.permalink
        doc["parentId"] = self.parent_id
        del doc["created_utc"]
        del doc["permalink"]
        del doc["parent_id"]
        return Comment(**doc)
