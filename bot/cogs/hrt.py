from typing import Literal

import discord
from catherinecore import Catherine
from discord import app_commands
from discord.ext import commands
from libs.cog_utils.hrt import (
    HRTType,
    build_hrt_embed,
    calc_e,
    calc_prog,
    calc_t,
)
from libs.utils import EstrogenEmbed, ProgEmbed, TestosteroneEmbed


class HRTConversion(commands.Cog):
    """Module to convert HRT units"""

    def __init__(self, bot: Catherine) -> None:
        self.bot = bot

    @app_commands.command(name="hrt-convert")
    @app_commands.describe(
        type="The type of HRT",
        amount="The amount you want to convert",
        units="The units to convert to. Note that pmol/L and pg/mL are only for E",
    )
    async def hrt_convert(
        self,
        interaction: discord.Interaction,
        type: Literal["Estradiol", "Progesterone", "Testosterone"],
        amount: app_commands.Range[int, 0, 5000],
        units: Literal["pmol/L", "pg/mL", "nmol/L", "ng/dL"],
    ) -> None:
        """Converts HRT types to other units"""
        master_lookup = {
            "Estradiol": {"constant": 3.6712337, "embed": EstrogenEmbed()},
            "Progesterone": {"constant": 3.18, "embed": ProgEmbed()},
            "Testosterone": {"constant": 0.0346703, "embed": TestosteroneEmbed()},
        }

        # Handle cases when people want to select E but the wrong units
        if type != HRTType.Estradiol.value and units in ["pmol/L", "pg/mL"]:
            await interaction.response.send_message(
                "The units `pmol/L` and `pg/mL` are only available for the type `Estradiol`"
            )
            return

        # The way Triona handles it is 3 different commands
        # I rather explicitly make them into one if/elif/else stack for clarity's sake
        if type == HRTType.Estradiol.value:
            e_values = calc_e(amount, master_lookup[type]["constant"], units)
            embed = build_hrt_embed(master_lookup[type]["embed"], e_values)
            await interaction.response.send_message(embed=embed)
        elif type == HRTType.Progesterone.value:
            prog_values = calc_prog(amount, master_lookup[type]["constant"], units)
            embed = build_hrt_embed(master_lookup[type]["embed"], prog_values)
            await interaction.response.send_message(embed=embed)
        else:
            t_values = calc_t(amount, master_lookup[type]["constant"], units)
            embed = build_hrt_embed(master_lookup[type]["embed"], t_values)
            await interaction.response.send_message(embed=embed)


async def setup(bot: Catherine) -> None:
    await bot.add_cog(HRTConversion(bot))
