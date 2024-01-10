import re


def format_link_references(content: str) -> str:
    keyword = content.split("=")[-1]
    keyword_length = len(keyword) + 1

    # Replace the broken parentheses with a quoted one
    url = content[:-keyword_length].replace(")", "%29").replace("(", "%28")
    return f"[{keyword}]({url})"


def format_pronouns_references(match: str) -> str:
    cleaned = re.sub(r"^/", "", match)
    parts = cleaned.split("=")
    link = f"https://en.pronouns.page/{parts[0]}".replace(" ", "%20")
    return f"[{parts[1]}]({link})"


# What this does is if it's a term starting with an "#",
# we strip that and give the result
def format_term_references(match: str):
    # For terms
    if match.startswith("#"):
        cleaned = re.sub(r"^#", "", match)
        parts = cleaned.split("=")
        link = f"https://en.pronouns.page/terminology#{parts[0]}".replace(" ", "%20")
        return f"[{parts[1]}]({link})"

    cleaned_link = f"https://en.pronouns.page/terminology#{match}".replace(" ", "%20")
    return f"[{match}]({cleaned_link})"


def format_inline_references(content: str):
    def _format_reference(match: re.Match):
        link_regex = re.compile(r"^(http|https)://")
        extracted_content = match.group(1)
        if link_regex.search(extracted_content) is not None:
            return format_link_references(extracted_content)
        elif extracted_content.startswith("/"):
            return format_pronouns_references(extracted_content)
        return format_term_references(extracted_content)

    regex = re.compile(r"{(.*?)}")
    return regex.sub(lambda match: _format_reference(match), content)


def format_multi_reference(content: str, sep: str = "|") -> str:
    if sep in content:
        parts = content.split(sep)
        formatted = "; ".join(format_inline_references(part) for part in parts)
        return f"({formatted})"
    return format_inline_references(content)
