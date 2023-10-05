from typing import Dict, Literal, Union

import discord

from .enums import HRTUnit


def calc_e(
    amount: int, constant: float, suggested_unit: str
) -> Dict[str, Union[Literal[0], float]]:
    pmol_l_output = 0
    pg_ml_output = 0

    if suggested_unit == HRTUnit.POML_L.value:
        pg_ml_output = amount / constant
    elif suggested_unit == HRTUnit.PG_ML.value:
        pmol_l_output = amount * constant

    return {"pmol_l_output": pmol_l_output, "pg_ml_output": pg_ml_output}


def calc_prog_or_t(
    amount: int, constant: float, suggested_unit: str
) -> Dict[str, Union[Literal[0], float]]:
    nmol_l_output = 0
    ng_dl_output = 0

    if suggested_unit == HRTUnit.NMOL_L.value:
        nmol_l_output = amount / constant
    elif suggested_unit == HRTUnit.NG_DL.value:
        ng_dl_output = amount * constant

    return {"nmol_l_output": nmol_l_output, "ng_dl_output": ng_dl_output}


def build_hrt_embed(
    embed: discord.Embed, values: Dict[str, Union[Literal[0], float]]
) -> discord.Embed:
    name_lookup = {
        "pmol_l_output": HRTUnit.POML_L.value,
        "pg_ml_output": HRTUnit.PG_ML.value,
        "nmol_l_output": HRTUnit.NMOL_L.value,
        "ng_dl_output": HRTUnit.NG_DL.value,
    }

    for key, value in values.items():
        embed.add_field(name=name_lookup[key], value=f"{value:.2f}")
    return embed
