import re
from typing import List, Optional, TypedDict

from yarl import URL

from .structs import (
    InclusiveContent,
    NounContent,
    NounEntity,
    PronounsEntity,
    PronounsMorphemes,
    TermAssets,
)


class PronounsInfo(TypedDict):
    title: str
    desc: str


def format_term_titles(title: str):
    title_list = title.split("|")
    return ", ".join(title_list).rstrip(",")


def format_title_options(title: str):
    title_list = title.split("|")
    return "\n".join([f"- **{title}**" for title in title_list])


def format_instead_of_options(options: str):
    options_list = options.split("|")
    return "\n".join([f"- ~~{options}~~" for options in options_list])


def format_pronouns_examples(examples: List[str], morphemes: PronounsMorphemes) -> str:
    values = morphemes.values()
    regex = re.compile(r"(%s)" % "|".join(map(re.escape, values)))
    subbed = [
        f"- {regex.sub(lambda match: f'**{match.group()}**', item)}"
        for item in examples
    ]
    return "\n".join(subbed)


def format_pronouns_info(entry: PronounsEntity) -> PronounsInfo:
    def format_table():
        data = entry.morphemes.to_dict()
        final_form = "\n".join(
            [f"- **{k.replace('_', ' ').title()}**: {v}" for k, v in data.items()]
        )
        return f"### Morphemes \n{final_form}"

    title = f"{entry.name}"
    desc = (
        f"(*{entry.description}*)",
        f"{format_table()}",
        f"### Examples \n{format_pronouns_examples(entry.examples, entry.morphemes)}",
        f"### History \n{format_inline_references(entry.history)}"
        if len(entry.history) != 0
        else "" f"### Source Info\n{format_inline_references(entry.sources_info)}"
        if entry.sources_info is not None
        else "",
    )
    final_desc = "\n".join(desc)
    return PronounsInfo(title=title, desc=final_desc)


def format_inclusive_content(content: InclusiveContent):
    final_content = (
        f"### Instead of \n{format_instead_of_options(content.instead_of)}",
        f"### Better Say\n{format_title_options(content.say)}",
        f"### Because\n{content.because}",
        f"### Clarification\n{content.clarification}"
        if content.clarification is not None
        else "",
    )

    return "\n".join(final_content)


def format_gender_neutral_content(content: NounEntity) -> str:
    def _format_internals(noun_content: NounContent) -> str:
        combined = f"{noun_content.regular}|{noun_content.plural}"
        if len(noun_content.plural) == 0:
            combined = noun_content.regular
        internals_list = combined.split("|")
        return "\n".join([f"- {item}" for item in internals_list])

    final_content = (
        f"### Masculine \n{_format_internals(content.masc)}",
        f"### Feminine \n{_format_internals(content.fem)}",
        f"### Neutral \n{_format_internals(content.neutral)}",
    )
    return "\n".join(final_content)


def format_greek_references(content: str) -> str:
    # Old Regex: ((?<=).+(?=\=)).+((?<=\=).+)$ (group 2 is the keyword, group 1 is the url)
    # This regex is removed due to polynomial backtracking exploits
    # This new way doesn't even use regex at all
    keyword = content.split("=")[-1]
    keyword_length = len(keyword) + 1

    # Replace the broken parentheses with a quoted one
    url = content[:-keyword_length].replace(")", "%29").replace("(", "%28")
    return f"[{keyword}]({url})"


def format_pronouns_references(content: str) -> str:
    parts = content.split("=")
    return f"[{parts[1]}](https://en.pronouns.page{parts[0]})"


def format_inline_references(content: str) -> str:
    regex = re.compile(r"(?<={).*?(?=})")
    extraction_regex = re.compile(r"(?<=#).*?(?=\=)")
    detect_link_regex = re.compile(r"^(http|https)://")

    def disambiguate(match: re.Match[str]):
        sub_match = extraction_regex.search(match.group())
        if sub_match is None:
            return match.group()
        return sub_match.group()

    def format_link(match: re.Match[str]):
        url_match = detect_link_regex.search(match.group())
        if url_match is not None:
            # More than likely it's those stupid greek definitions
            return format_greek_references(match.group())
        elif match.group().startswith("/"):
            return format_pronouns_references(match.group())

        link = f"https://en.pronouns.page/terminology#{disambiguate(match)}".replace(
            " ", "%20"
        )
        return f"[{disambiguate(match)}]({link})"

    return regex.sub(lambda match: format_link(match), content)


def split_flags(content: str) -> List[str]:
    regex = re.compile(r"(?<=\[).*?(?=\])")
    return regex.findall(content)


def determine_author(author: Optional[str]) -> str:
    author_base_url = URL("https://pronouns.page/")
    if author is None:
        return "Unknown"
    author_link = str(author_base_url / f"@{author}")
    return f"[{author}]({author_link})"


def determine_image_url(assets: TermAssets) -> str:
    if len(assets.flags[0]) != 0:
        base_flags_url = URL("https://en.pronouns.page/flags/")
        asset = assets.flags[0].replace('"', "")
        complete_url = (
            base_flags_url / f"{asset}.png"
        )  # Always grab the first one bc i doubt there are two or more flags
        return str(complete_url)
    else:
        # Apparently the "[object Object]" thing is a pronouns.page bug
        if assets.images is None or "[object Object]" in assets.images:
            return ""

        # If there isn't a flag, then it's probably a custom one
        base_cdn_asset = URL("https://dclu0bpcdglik.cloudfront.net/images/")
        asset = assets.images.split(",")
        image_file = f"{asset[0]}-flag.png"
        return str(base_cdn_asset / image_file)
