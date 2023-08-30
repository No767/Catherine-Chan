import sys
from pathlib import Path

another_path = Path(__file__).parents[2].joinpath("bot")
sys.path.append(str(another_path))

from libs.cog_utils.profiles import parse_values, present_info, snake_case_to_title

RECORD = {"id": 454357482102587393, "views": 0, "name": "Noelle"}


def test_snake_case_to_title():
    assert snake_case_to_title("hello_world") == "Hello World"
    assert snake_case_to_title("hello_world_hello") == "Hello World Hello"
    assert snake_case_to_title("hello") == "Hello"
    assert snake_case_to_title("hello_world_hello_world") == "Hello World Hello World"


def test_parse_values_none():
    val = parse_values(None)
    assert val == "None"


def test_parse_values_int():
    val = parse_values(4)
    assert val == "4"


def test_parse_values_string():
    val = parse_values("hello")
    assert val == "Hello"


def test_present_info():
    info = present_info(RECORD)
    assert info == "\n**Name**: Noelle"
