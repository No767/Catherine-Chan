import discord
from catherinecore import Catherine
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands
from libs.cog_utils.hrt import calc_e, calc_prog, calc_prolac, calc_t
from libs.cog_utils.hrt.embeds import (
    EstrogenEmbed,
    ProgEmbed,
    ProlactinEmbed,
    TestosteroneEmbed,
)


class HRTConversion(commands.GroupCog, group_name="hrt-convert"):
    """Module to convert HRT units"""

    def __init__(self, bot: Catherine) -> None:
        self.bot = bot
        super().__init__()

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
        results = calc_e(amount, units.value)

        pmol_l_output = results["pmol_l"]
        pg_ml_output = results["pg_ml"]

        embed = EstrogenEmbed()
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
        res = calc_prog(amount, units.value)

        nmol_l = res["nmol_l"]
        ng_ml = res["ng_ml"]

        embed = ProgEmbed()
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
        res = calc_t(amount, units.value)

        nmol_l = res["nmol_l"]
        ng_dl = res["ng_dl"]

        embed = TestosteroneEmbed()
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
        res = calc_prolac(amount, units.value)

        miu_l = res["miu_l"]
        ng_ml = res["ng_ml"]

        embed = ProlactinEmbed()
        embed.add_field(name="mIU/L", value=f"{miu_l:.2f}")
        embed.add_field(name="ng/mL", value=f"{ng_ml:.2f}")
        await interaction.response.send_message(embed=embed)


async def setup(bot: Catherine) -> None:
    await bot.add_cog(HRTConversion(bot))
