from typing import List, Optional, TypedDict, Union

import msgspec


class DictTermsEntry(msgspec.Struct):
    term: str
    original: Union[str, None]
    definition: str
    locale: str
    flags: str
    category: str


class DictInclusiveEntry(msgspec.Struct):
    instead_of: str
    say: str
    because: str
    categories: str
    clarification: Union[str, None]


class DictNounsEntry(msgspec.Struct):
    masc: str
    fem: str
    neutr: str
    masc_plural: str
    fem_plural: str
    neutr_plural: str


class DictPronounsPageLaDiffEntry(TypedDict):
    term: str
    original: Union[str, None]
    definition: str
    locale: str
    approved: int
    base_id: Optional[str]
    author_id: str
    deleted: int
    flags: List[str]
    category: str
    key: str
    author: str


class DictPronounsPageEntry(TypedDict):
    term: str
    original: Union[str, None]
    definition: str
    locale: str
    approved: int
    base_id: Optional[str]
    author_id: str
    deleted: int
    flags: List[str]
    category: str
    key: str
    author: str
    versions: List[DictPronounsPageLaDiffEntry]
