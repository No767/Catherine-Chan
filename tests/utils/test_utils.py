import sys
from pathlib import Path

another_path = Path(__file__).parents[2].joinpath("bot")
sys.path.append(str(another_path))

from libs.utils import is_docker


def test_is_docker():
    if is_docker() is False:
        assert is_docker() is False
        return
    assert is_docker() is True
