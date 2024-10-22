from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

import discord
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands

if TYPE_CHECKING:
    from catherinecore import Catherine

ESTRADIOL = 3.6712337
PROGESTERONE = 3.18
PROLACTIN = 21.2765957446809
TESTOSTERONE = 0.0346703

### Structs

# Although msgspec structs can be used, the original code relies on dicts.
# In order to preserve the current implementation, dicts will be used instead


class EstradiolResults(TypedDict):
    pmol_l: float
    pg_ml: float


class TestosteroneResults(TypedDict):
    nmol_l: float
    ng_dl: float


class ProgesteroneResults(TypedDict):
    nmol_l: float
    ng_ml: float


class ProlactinResults(TypedDict):
    miu_l: float
    ng_ml: float


class HRTConversion(commands.GroupCog, group_name="hrt-convert"):
    """Module to convert HRT units"""

    def __init__(self, bot: Catherine) -> None:
        self.bot = bot
        super().__init__()

    ### Calculation utilities

    # Current measurements:
    # E: pmol/L, pg/mL
    # Prog: nmol/L, ng/dL (convert to ng/mL, which is ng/dl * 0.01 = ng/mL)
    # T: nmol/L, ng/dL

    def calc_estradiol(self, amount: int, unit: str) -> EstradiolResults:
        output = EstradiolResults(pmol_l=0.0, pg_ml=0.0)
        output[unit] = amount

        if unit == "pmol_l":
            output["pg_ml"] = amount / ESTRADIOL
        elif unit == "pg_ml":
            output["pmol_l"] = amount * ESTRADIOL

        return output

    def calc_testosterone(self, amount: int, unit: str) -> TestosteroneResults:
        output = TestosteroneResults(nmol_l=0.0, ng_dl=0.0)
        output[unit] = amount

        if unit == "nmol_l":
            output["ng_dl"] = amount / TESTOSTERONE
        elif unit == "ng_dl":
            output["nmol_l"] = amount * TESTOSTERONE

        return output

    def calc_progesterone(self, amount: int, unit: str) -> ProgesteroneResults:
        output = ProgesteroneResults(nmol_l=0.0, ng_ml=0.0)
        output[unit] = amount

        if unit == "nmol_l":
            # Since apparently Triona's code converts ng/dL to ng/mL, the conversion rate is basically ng/dl * 0.01 = ng/mL
            output["ng_ml"] = amount / PROGESTERONE
        elif unit == "ng_ml":
            output["nmol_l"] = amount * PROGESTERONE

        return output

    def calc_prolactin(self, amount: int, unit: str) -> ProlactinResults:
        output = ProlactinResults(miu_l=0.0, ng_ml=0.0)

        output[unit] = amount

        if unit == "miu_l":
            output["ng_ml"] = amount / PROLACTIN
        elif unit == "ng_ml":
            output["miu_l"] = amount * PROLACTIN

        return output

    @app_commands.command(name="estradiol")
    @app_commands.describe(
        amount="The amount to convert", units="The estradiol unit to convert from"
    )
    @app_commands.choices(
        units=[
            Choice(name="pmol/L", value="pmol_l"),
            Choice(name="pg/mL", value="pg_ml"),
        ]
    )
    async def estradiol(
        self, interaction: discord.Interaction, amount: int, units: Choice[str]
    ) -> None:
        """Converts one unit of estradiol to another unit"""
        results = self.calc_estradiol(amount, units.value)

        pmol_l_output = results["pmol_l"]
        pg_ml_output = results["pg_ml"]

        embed = discord.Embed(
            title="Estradiol Level Conversions", color=discord.Color.from_str("#F7A8B8")
        )
        embed.add_field(name="pmol/L", value=f"{pmol_l_output:.2f}")
        embed.add_field(name="pg/mL", value=f"{pg_ml_output:.2f}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="testosterone")
    @app_commands.describe(
        amount="The amount to convert to", units="The testosterone unit to convert from"
    )
    @app_commands.choices(
        units=[
            Choice(name="nmol/L", value="nmol_l"),
            Choice(name="ng/dL", value="ng_dl"),
        ]
    )
    async def testosterone(self, interaction: discord.Interaction, amount: int, units: Choice[str]):
        """Converts one unit of testosterone to another unit"""
        res = self.calc_testosterone(amount, units.value)

        nmol_l = res["nmol_l"]
        ng_dl = res["ng_dl"]

        embed = discord.Embed(
            title="Testosterone Level Conversions",
            color=discord.Color.from_str("#55CDFC"),
        )
        embed.add_field(name="nmol/L", value=f"{nmol_l:.2f}")
        embed.add_field(name="ng/dL", value=f"{ng_dl:.2f}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="progesterone")
    @app_commands.describe(
        amount="The amount to convert", units="The progesterone unit to convert from"
    )
    @app_commands.choices(
        units=[
            Choice(name="nmol/L", value="nmol_l"),
            Choice(name="ng/dL", value="ng_ml"),
        ]
    )
    async def progesterone(
        self, interaction: discord.Interaction, amount: int, units: Choice[str]
    ) -> None:
        """Converts one unit of progesterone to another unit"""
        res = self.calc_progesterone(amount, units.value)

        nmol_l = res["nmol_l"]
        ng_ml = res["ng_ml"]

        embed = discord.Embed(
            title="Progesterone Level Conversions",
            color=discord.Color.from_str("#FFFFFF"),
        )
        embed.add_field(name="nmol/L", value=f"{nmol_l:.2f}")
        embed.add_field(name="ng/dL", value=f"{ng_ml:.2f}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="prolactin")
    @app_commands.describe(
        amount="The amount to convert to", units="The prolactin unit to convert from"
    )
    @app_commands.choices(
        units=[Choice(name="mIU/L", value="miu_l"), Choice(name="ng/mL", value="ng_ml")]
    )
    async def prolactin(self, interaction: discord.Interaction, amount: int, units: Choice[str]):
        """Converts one unit of prolactin to another unit"""
        res = self.calc_prolactin(amount, units.value)

        miu_l = res["miu_l"]
        ng_ml = res["ng_ml"]

        embed = discord.Embed(
            title="Prolactin Level Conversions", color=discord.Color.from_str("#9C59D1")
        )
        embed.add_field(name="mIU/L", value=f"{miu_l:.2f}")
        embed.add_field(name="ng/mL", value=f"{ng_ml:.2f}")
        await interaction.response.send_message(embed=embed)


async def setup(bot: Catherine) -> None:
    await bot.add_cog(HRTConversion(bot))
