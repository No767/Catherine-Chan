from typing import Union

import discord

from .enums import HRTUnit
from .structs import EResults, ProgResults, TResults

# Current measurements:
# E: pmol/L, pg/mL
# Prog: nmol/L, ng/dL (convert to ng/mL, which is ng/dl * 0.01 = ng/mL)
# T: nmol/L, ng/dL


def calc_e(amount: int, constant: float, suggested_unit: str) -> EResults:
    pmol_l_output = 0.0
    pg_ml_output = 0.0

    if suggested_unit == HRTUnit.POML_L.value:
        pg_ml_output = amount / constant
    elif suggested_unit == HRTUnit.PG_ML.value:
        pmol_l_output = amount * constant

    return EResults(pmol_l_output=pmol_l_output, pg_ml_output=pg_ml_output)


def calc_t(amount: int, constant: float, suggested_unit: str) -> TResults:
    nmol_l_output = 0.0
    ng_dl_output = 0.0

    if suggested_unit == HRTUnit.NMOL_L.value:
        nmol_l_output = amount / constant
    elif suggested_unit == HRTUnit.NG_DL.value:
        ng_dl_output = amount * constant

    return TResults(nmol_l_output=nmol_l_output, ng_dl_output=ng_dl_output)


def calc_prog(amount: int, constant: float, suggested_unit: str) -> ProgResults:
    nmol_l_output = 0.0
    ng_ml_output = 0.0

    if suggested_unit == HRTUnit.NMOL_L.value:
        nmol_l_output = amount / constant

    # Since apparently Triona's code converts ng/dL to ng/mL, the conversion rate is basically ng/dl * 0.01 = ng/mL
    elif suggested_unit == HRTUnit.NG_DL.value:
        ng_ml_output = (
            amount * constant
        ) * 0.01  # Do not blame Noelle if this is incorrect.

    return ProgResults(ng_ml_output=ng_ml_output, nmol_l_output=nmol_l_output)


def build_hrt_embed(
    embed: discord.Embed, values: Union[EResults, ProgResults, TResults]
) -> discord.Embed:
    name_lookup = {
        "pmol_l_output": HRTUnit.POML_L.value,
        "pg_ml_output": HRTUnit.PG_ML.value,
        "nmol_l_output": HRTUnit.NMOL_L.value,
        "ng_dl_output": HRTUnit.NG_DL.value,
        "ng_ml_output": HRTUnit.NG_ML.value,
    }

    for key, value in values.items():
        embed.add_field(name=name_lookup[key], value=f"{value:.2f}")
    return embed
