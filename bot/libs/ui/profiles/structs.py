from typing import TypedDict


class SimpleProfileEntry(TypedDict):
    user_id: int
    name: str
    pronouns: str


class SimpleViewsEntry(TypedDict):
    user_id: int
    name: str
    views: int
