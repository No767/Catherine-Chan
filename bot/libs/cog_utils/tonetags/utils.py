import re
from typing import List, Union

from .structs import SimilarTonetags


def parse_tonetag(tonetag: str) -> str:
    """Parses a tonetag properly and sends back the stripped results

    Args:
        tonetag (str): Tonetag

    Returns:
        str: Parsed and cleaned up result
    """
    return re.sub(r"^/", "", tonetag, re.IGNORECASE)


def format_similar_tonetags(rows: Union[List[SimilarTonetags], None]) -> str:
    """Formats a list of similar tonetags into a string for the user to see

    Parameters
    ----------
    rows : Union[List[SimilarTonetags], None]
        List of similar tonetags or None

    Returns
    -------
    str
        Formatted string for the end user
    """
    if rows is None or len(rows) == 0:
        return "No tonetags found"

    names = "\n".join([row["indicator"] for row in rows])
    return f"Tonetag not found. Did you mean:\n{names}"
