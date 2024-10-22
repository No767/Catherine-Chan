import pytest
from cogs.pride_profiles import PrideProfiles, format_title


@pytest.fixture
def cog(bot) -> PrideProfiles:
    return PrideProfiles(bot)


@pytest.fixture
def filled_rows() -> list[dict[str, str]]:
    return [{"name": "Noelle"}, {"name": "Noel"}]


@pytest.fixture
def empty_rows() -> list:
    return []


def test_format_title(cog: PrideProfiles):
    assert format_title("gender_identity") == "Gender Identity"
    assert format_title("sexual_orientation") == "Sexual Orientation"


def test_disambiguate(cog: PrideProfiles, filled_rows: list[dict[str, str]], empty_rows: list):
    filled = cog.disambiguate(filled_rows)
    assert filled.startswith("Profile not found. Did you mean...")

    empty = cog.disambiguate(empty_rows)
    nonexistent = cog.disambiguate(None)
    assert "Profile not found." in (empty, nonexistent)
