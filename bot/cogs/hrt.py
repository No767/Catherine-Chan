import discord
from catherinecore import Catherine
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands
from libs.types import hrt

ESTRADIOL = 3.6712337
PROGESTERONE = 3.18
PROLACTIN = 21.2765957446809
TESTOSTERONE = 0.0346703


class HRTConversion(commands.GroupCog, group_name="hrt-convert"):
    """Module to convert HRT units"""

    def __init__(self, bot: Catherine) -> None:
        self.bot = bot
        super().__init__()

    def calc_e(self, amount: int, unit: str) -> hrt.EResults:
        output = hrt.EResults(pmol_l=0.0, pg_ml=0.0)
        output[unit] = amount

        if unit == "pmol_l":
            output["pg_ml"] = amount / ESTRADIOL
        elif unit == "pg_ml":
            output["pmol_l"] = amount * ESTRADIOL

        return output

    def calc_prolac(self, amount: int, unit: str) -> hrt.ProlacResults:
        output = hrt.ProlacResults(miu_l=0.0, ng_ml=0.0)

        output[unit] = amount

        if unit == "miu_l":
            output["ng_ml"] = amount / PROLACTIN
        elif unit == "ng_ml":
            output["miu_l"] = amount * PROLACTIN

        return output

    def calc_t(self, amount: int, unit: str) -> hrt.TResults:
        output = hrt.TResults(nmol_l=0.0, ng_dl=0.0)
        output[unit] = amount

        if unit == "nmol_l":
            output["ng_dl"] = amount / TESTOSTERONE
        elif unit == "ng_dl":
            output["nmol_l"] = amount * TESTOSTERONE

        return output

    def calc_prog(self, amount: int, unit: str) -> hrt.ProgResults:
        output = hrt.ProgResults(nmol_l=0.0, ng_ml=0.0)
        output[unit] = amount

        if unit == "nmol_l":
            # Since apparently Triona's code converts ng/dL to ng/mL, the conversion rate is basically ng/dl * 0.01 = ng/mL
            output["ng_ml"] = amount / PROGESTERONE
        elif unit == "ng_ml":
            output["nmol_l"] = amount * PROGESTERONE

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
        results = self.calc_e(amount, units.value)

        pmol_l_output = results["pmol_l"]
        pg_ml_output = results["pg_ml"]

        embed = discord.Embed(
            title="Estradiol Level Conversions", color=discord.Color.from_str("#F7A8B8")
        )
        embed.add_field(name="pmol/L", value=f"{pmol_l_output:.2f}")
        embed.add_field(name="pg/mL", value=f"{pg_ml_output:.2f}")
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
        res = self.calc_prog(amount, units.value)

        nmol_l = res["nmol_l"]
        ng_ml = res["ng_ml"]

        embed = discord.Embed(
            title="Progesterone Level Conversions",
            color=discord.Color.from_str("#FFFFFF"),
        )
        embed.add_field(name="nmol/L", value=f"{nmol_l:.2f}")
        embed.add_field(name="ng/dL", value=f"{ng_ml:.2f}")
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
    async def testosterone(
        self, interaction: discord.Interaction, amount: int, units: Choice[str]
    ):
        """Converts one unit of testosterone to another unit"""
        res = self.calc_t(amount, units.value)

        nmol_l = res["nmol_l"]
        ng_dl = res["ng_dl"]

        embed = discord.Embed(
            title="Testosterone Level Conversions",
            color=discord.Color.from_str("#55CDFC"),
        )
        embed.add_field(name="nmol/L", value=f"{nmol_l:.2f}")
        embed.add_field(name="ng/dL", value=f"{ng_dl:.2f}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="prolactin")
    @app_commands.describe(
        amount="The amount to convert to", units="The prolactin unit to convert from"
    )
    @app_commands.choices(
        units=[Choice(name="mIU/L", value="miu_l"), Choice(name="ng/mL", value="ng_ml")]
    )
    async def prolactin(
        self, interaction: discord.Interaction, amount: int, units: Choice[str]
    ):
        """Converts one unit of prolactin to another unit"""
        res = self.calc_prolac(amount, units.value)

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
