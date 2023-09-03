import datetime
from typing import TypedDict


class ToneTagInfo(TypedDict):
    indicator: str
    definition: str
    created_at: datetime.datetime
    author_id: int
    tonetags_id: int


class SimpleToneTag(TypedDict):
    indicator: str
    author_id: int
    tonetags_id: int


class BareToneTag(TypedDict):
    indicator: str
    tonetags_id: int
