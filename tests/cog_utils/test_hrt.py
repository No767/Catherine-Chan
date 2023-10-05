import sys
from math import isclose
from pathlib import Path

another_path = Path(__file__).parents[2].joinpath("bot")
sys.path.append(str(another_path))

from libs.cog_utils.hrt import build_hrt_embed, calc_e, calc_prog_or_t
from libs.utils import EstrogenEmbed

E_CONSTANT = 3.6712337
PROG_CONSTANT = 3.18
T_CONSTANT = 0.0346703
AMOUNT = 2

POML_L = "pmol/L"
PG_ML = "pg/mL"
NMOL_L = "nmol/L"
NG_DL = "ng/dL"


def test_calc_e_poml():
    res = calc_e(AMOUNT, E_CONSTANT, POML_L)
    assert res["pmol_l_output"] == 0 and res["pg_ml_output"] == 0.544775997234935

    second_res = calc_e(AMOUNT, E_CONSTANT, PG_ML)
    assert (
        isclose(second_res["pmol_l_output"], 7.3424674)
        and second_res["pg_ml_output"] == 0
    )


def test_calc_prog():
    res = calc_prog_or_t(AMOUNT, PROG_CONSTANT, NMOL_L)
    assert (
        isclose(res["nmol_l_output"], 0.6289308176100629) and res["ng_dl_output"] == 0
    )

    second_res = calc_prog_or_t(AMOUNT, PROG_CONSTANT, NG_DL)
    assert (
        isclose(second_res["ng_dl_output"], 6.36) and second_res["nmol_l_output"] == 0
    )


def test_calc_t():
    res = calc_prog_or_t(AMOUNT, T_CONSTANT, NMOL_L)
    assert isclose(res["nmol_l_output"], 57.68626172833809) and res["ng_dl_output"] == 0

    second_res = calc_prog_or_t(AMOUNT, T_CONSTANT, NG_DL)
    assert (
        isclose(second_res["ng_dl_output"], 0.0693406)
        and second_res["nmol_l_output"] == 0
    )


def test_build_hrt_embed():
    embed = EstrogenEmbed()
    res = calc_e(AMOUNT, E_CONSTANT, POML_L)
    built_embed = build_hrt_embed(embed, res)

    embed_but_dict = built_embed.to_dict()

    assert embed_but_dict["title"] == "Estradiol Level Conversions"

    fields = embed_but_dict["fields"]

    assert (
        fields[0]["name"] == POML_L
        and fields[0]["value"] == f'{res["pmol_l_output"]:.2f}'
    ) and (
        fields[1]["name"] == PG_ML
        and fields[1]["value"] == f'{res["pg_ml_output"]:.2f}'
    )
