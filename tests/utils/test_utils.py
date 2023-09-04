import sys
from pathlib import Path

another_path = Path(__file__).parents[2].joinpath("bot")
sys.path.append(str(another_path))

ENV_PATH = another_path / ".env"

from libs.utils import is_docker, read_env


def test_is_docker():
    if is_docker() is False:
        assert is_docker() is False
        return
    assert is_docker() is True


def test_read_env():
    if is_docker():
        config = read_env(ENV_PATH)
        assert config["SHELL"] == "/bin/bash" or "/bin/zsh"
        return
    config = read_env(ENV_PATH)
    assert isinstance(config, dict)
