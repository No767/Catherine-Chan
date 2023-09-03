from typing import Any, Dict

from discord.utils import format_dt

from .structs import BareToneTag, SimpleToneTag, ToneTagInfo


class ToneTagInfoPageEntry:
    __slots__ = ["indicator", "definition", "created_at", "author_id", "tonetags_id"]

    def __init__(self, entry: ToneTagInfo):
        self.indicator = entry["indicator"]
        self.definition = entry["definition"]
        self.created_at = entry["created_at"]
        self.author_id = entry["author_id"]
        self.tonetags_id = entry["tonetags_id"]

    def to_dict(self) -> Dict[str, Any]:
        data = {
            "title": f"/{self.indicator}",
            "description": self.definition,
            "fields": [
                {"name": "ID", "value": self.tonetags_id, "inline": True},
                {"name": "Author ", "value": f"<@{self.author_id}>", "inline": True},
                {
                    "name": "Created At",
                    "value": format_dt(self.created_at),
                    "inline": True,
                },
            ],
        }
        return data


class SimpleToneTagPageEntry:
    __slots__ = ("indicator", "author_id", "tonetags_id")

    def __init__(self, entry: SimpleToneTag):
        self.indicator = entry["indicator"]
        self.author_id = entry["author_id"]
        self.tonetags_id = entry["tonetags_id"]

    def __str__(self) -> str:
        return (
            f"/{self.indicator} (ID: {self.tonetags_id}, Creator: <@{self.author_id}>)"
        )


class BareToneTagPageEntry:
    __slots__ = ("indicator", "tonetags_id")

    def __init__(self, entry: BareToneTag):
        self.indicator = entry["indicator"]
        self.tonetags_id = entry["tonetags_id"]

    def __str__(self) -> str:
        return f"/{self.indicator} (ID: {self.tonetags_id})"
