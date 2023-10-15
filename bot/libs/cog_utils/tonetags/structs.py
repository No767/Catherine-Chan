import datetime
from typing import TypedDict


class TonetagInfo(TypedDict):
    indicator: str
    definition: str
    created_at: datetime.datetime
    author_id: int
    uses: int
    tonetags_id: int


class SimilarTonetags(TypedDict):
    indicator: str


class ExactAndSimilarTonetags(TypedDict):
    indicator: str
    definition: str


# Here to avoid circular imports
class StatsBareToneTag(TypedDict):
    indicator: str
    uses: int
    tonetags_id: int
