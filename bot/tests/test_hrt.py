from math import isclose

import pytest
from cogs.hrt import HRTConversion

AMOUNT = 200


@pytest.fixture
def cog(bot) -> HRTConversion:
    return HRTConversion(bot)


def test_calc_estradiol(cog: HRTConversion):
    pm_convert = cog.calc_estradiol(AMOUNT, "pmol_l")
    pg_convert = cog.calc_estradiol(AMOUNT, "pg_ml")

    assert isclose(pm_convert["pmol_l"], AMOUNT) and isclose(
        pm_convert["pg_ml"], 54.47759972349349
    )
    assert isclose(pg_convert["pmol_l"], 734.24674) and isclose(
        pg_convert["pg_ml"], AMOUNT
    )


def test_calc_testosterone(cog: HRTConversion):
    nm_convert = cog.calc_testosterone(AMOUNT, "nmol_l")
    ng_convert = cog.calc_testosterone(AMOUNT, "ng_dl")

    assert isclose(nm_convert["nmol_l"], 200) and isclose(
        nm_convert["ng_dl"], 5768.626172833809
    )
    assert isclose(ng_convert["nmol_l"], 6.934060000000001) and isclose(
        ng_convert["ng_dl"], 200
    )


def test_calc_progesterone(cog: HRTConversion):
    nm_convert = cog.calc_progesterone(AMOUNT, "nmol_l")
    ng_convert = cog.calc_progesterone(AMOUNT, "ng_ml")

    assert isclose(nm_convert["nmol_l"], 200) and isclose(
        nm_convert["ng_ml"], 62.893081761006286
    )
    assert isclose(ng_convert["nmol_l"], 636.0) and isclose(ng_convert["ng_ml"], 200)


def test_calc_prolactin(cog: HRTConversion):
    miu_convert = cog.calc_prolactin(AMOUNT, "miu_l")
    ng_convert = cog.calc_prolactin(AMOUNT, "ng_ml")

    assert isclose(miu_convert["miu_l"], AMOUNT) and isclose(
        miu_convert["ng_ml"], 9.399999999999979
    )
    assert isclose(ng_convert["miu_l"], 4255.31914893618) and isclose(
        ng_convert["ng_ml"], AMOUNT
    )
