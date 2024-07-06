import pytest
from cogs.hrt import HRTConversion


@pytest.fixture
def cog(bot) -> HRTConversion:
    return HRTConversion(bot)


def test_calc_e(cog: HRTConversion):
    # In order not to return an exit code 5 from pytest
    # we just make an mock test
    pass
