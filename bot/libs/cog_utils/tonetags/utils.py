import re
from typing import Dict, List, Union


def parse_tonetag(tonetag: str) -> str:
    """Parses a tonetag properly and sends back the stripped results

    Args:
        tonetag (str): Tonetag

    Returns:
        str: Parsed and cleaned up result
    """
    return re.sub(r"^/", "", tonetag, re.IGNORECASE)


def format_options(rows: Union[List[Dict[str, str]], None]) -> str:
    if rows is None or len(rows) == 0:
        return "No tonetags found"

    names = "\n".join([row["indicator"] for row in rows])
    return f"Tonetag not found. Did you mean:\n{names}"
