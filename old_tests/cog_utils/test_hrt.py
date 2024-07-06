import sys
from math import isclose
from pathlib import Path

another_path = Path(__file__).parents[2].joinpath("bot")
sys.path.append(str(another_path))

from libs.cog_utils.hrt import calc_e, calc_prog, calc_prolac, calc_t

AMOUNT = 2

# For Estradiol
PMOL_L = "pmol_l"
PG_ML = "pg_ml"

# For Prolactin
MIU_L = "miu_l"
NG_ML = "ng_ml"

# For T and Prog
NMOL_L = "nmol_l"
NG_DL = "ng_dl"
NG_ML = "ng_ml"


def test_calc_e():
    res = calc_e(AMOUNT, PMOL_L)
    assert isclose(res["pmol_l"], 2.00) and isclose(res["pg_ml"], 0.544775997234935)

    second_res = calc_e(AMOUNT, PG_ML)
    assert isclose(second_res["pmol_l"], 7.3424674) and isclose(
        second_res["pg_ml"], 2.00
    )


def test_calc_prolac():
    res = calc_prolac(AMOUNT, MIU_L)
    assert isclose(res["miu_l"], 2) and isclose(res["ng_ml"], 0.09399999999999978)

    second_res = calc_prolac(AMOUNT, NG_ML)
    assert isclose(second_res["miu_l"], 42.5531914893618) and isclose(
        second_res["ng_ml"], 2.00
    )


def test_calc_t():
    res = calc_t(AMOUNT, NMOL_L)
    assert isclose(res["nmol_l"], 2.00) and isclose(res["ng_dl"], 57.68626172833809)

    second_res = calc_t(AMOUNT, NG_DL)
    assert isclose(second_res["nmol_l"], 0.0693406) and isclose(
        second_res["ng_dl"], 2.00
    )


def test_calc_prog():
    res = calc_prog(AMOUNT, NMOL_L)
    assert isclose(res["nmol_l"], 2.00) and isclose(res["ng_ml"], 0.6289308176100629)

    second_res = calc_prog(AMOUNT, NG_ML)
    assert isclose(second_res["nmol_l"], 6.36) and isclose(second_res["ng_ml"], 2)
