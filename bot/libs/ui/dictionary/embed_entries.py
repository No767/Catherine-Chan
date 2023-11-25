import re

from .structs import InclusiveEntity, NounEntity, PronounsEntity, TermEntity
from .utils import (
    determine_author,
    determine_image_url,
    format_gender_neutral_content,
    format_inclusive_content,
    format_inline_references,
    format_pronouns_info,
    format_term_titles,
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


class TermEntityEntry:
    __slots__ = (
        "term",
        "original",
        "definition",
        "key",
        "assets",
        "category",
        "author",
    )

    def __init__(self, entry: TermEntity):
        self.term = entry.term
        self.original = entry.original
        self.definition = entry.definition
        self.key = entry.key
        self.assets = entry.assets
        self.category = entry.category
        self.author = entry.author

    def to_dict(self):
        dirty_original = (
            f"({format_term_titles(format_inline_references(self.original))})"
            if self.original is not None
            else ""
        )
        cleaning_regex = re.compile(r"\{|\}")
        possible_image_url = determine_image_url(self.assets)
        possible_author = determine_author(self.author)
        title = format_term_titles(self.term)
        formatted_original = format_inline_references(
            cleaning_regex.sub("", dirty_original)
        )
        formatted_def = cleaning_regex.sub(
            "", format_inline_references(self.definition)
        ).capitalize()
        formatted_category = ", ".join(self.category).rstrip(",")
        desc = f"""
        {formatted_original}
        
        {formatted_def}
        """
        data = {
            "title": title,
            "description": desc,
            "thumbnail": possible_image_url,
            "fields": [
                {"name": "Author", "value": possible_author, "inline": True},
                {"name": "Category", "value": formatted_category, "inline": True},
            ],
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
