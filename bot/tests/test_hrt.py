import pytest
from cogs.hrt import HRTConversion


@pytest.fixture
def cog(bot) -> HRTConversion:
    return HRTConversion(bot)
