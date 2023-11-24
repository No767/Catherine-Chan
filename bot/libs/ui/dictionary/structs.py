from typing import List, Optional

import msgspec


class InclusiveContent(msgspec.Struct):
    instead_of: str
    say: str
    because: str
    clarification: Optional[str]


class InclusiveEntity(msgspec.Struct):
    content: InclusiveContent
    author: Optional[str]


class TermAssets(msgspec.Struct):
    flags: List[str]
    images: Optional[str]


class TermEntity(msgspec.Struct):
    term: str
    original: Optional[str]
    definition: str
    key: str
    assets: TermAssets
    category: List[str]
    author: Optional[str]


class NounContent(msgspec.Struct):
    regular: str
    plural: str


class NounEntity(msgspec.Struct):
    masc: NounContent
    fem: NounContent
    neutral: NounContent
    author: Optional[str]
