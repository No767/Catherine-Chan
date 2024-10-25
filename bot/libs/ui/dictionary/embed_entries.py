from .structs import InclusiveEntity, NounEntity, PronounsEntity
from .utils import (
    determine_author,
    format_gender_neutral_content,
    format_inclusive_content,
    format_pronouns_info,
)


class InclusiveEntityEntry:
    __slots__ = ("content", "author", "author_base_url")

    def __init__(self, entry: InclusiveEntity):
        self.content = entry.content
        self.author = entry.author

    def to_dict(self):
        desc = format_inclusive_content(self.content)
        data = {
            "description": desc,
            "fields": [{"name": "Author", "value": determine_author(self.author)}],
        }
        return data


class NounEntityEntry:
    __slots__ = ("entry", "author")

    def __init__(self, entry: NounEntity):
        self.entry = entry
        self.author = entry.author

    def to_dict(self):
        desc = format_gender_neutral_content(self.entry)
        possible_author = determine_author(self.author)

        data = {
            "description": desc,
            "fields": [{"name": "Author", "value": possible_author, "inline": True}],
        }
        return data


class PronounsEntityEntry:
    __slots__ = ("entry", "history", "sources_info")

    def __init__(self, entry: PronounsEntity):
        self.entry = entry
        self.history = self.entry.history
        self.sources_info = self.entry.sources_info

    def to_dict(self):
        info = format_pronouns_info(self.entry)
        data = {
            "title": info["title"],
            "description": info["desc"],
            "fields": [
                {
                    "name": "Aliases",
                    "value": ", ".join(self.entry.aliases).rstrip(","),
                    "inline": True,
                },
                {"name": "Normative", "value": self.entry.normative, "inline": True},
            ],
        }
        return data
