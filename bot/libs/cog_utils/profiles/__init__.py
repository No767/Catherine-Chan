from typing import Any, Dict


def snake_case_to_title(string: str) -> str:
    spilt_string = string.split("_")
    return " ".join([word.capitalize() for word in spilt_string])


def parse_values(value: Any) -> str:
    if value is None:
        return "None"
    elif isinstance(value, int):
        return str(value)
    return value.capitalize()


def present_info(record: Dict[str, Any]):
    separated_values = [
        f"**{snake_case_to_title(k)}**: {parse_values(v)}"
        for k, v in record.items()
        if k not in ["id", "views"]
    ]
    desc = "\n"
    joined_values = "\n".join(separated_values)
    desc += joined_values
    return desc
