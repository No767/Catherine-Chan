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


class PronounsMorphemes(msgspec.Struct):
    pronoun_subject: str
    pronoun_object: str
    possessive_determiner: str
    possessive_pronoun: str
    reflexive: str

    def to_dict(self):
        return {f: getattr(self, f) for f in self.__struct_fields__}

    def values(self) -> List[str]:
        return [getattr(self, f) for f in self.__struct_fields__]


class PronounsEntity(msgspec.Struct):
    name: str
    canonical_name: str
    description: str
    aliases: List[str]
    normative: bool
    morphemes: PronounsMorphemes
    examples: List[str]
    history: str
    sources_info: Optional[str]
