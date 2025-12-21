from __future__ import annotations

from typing import TYPE_CHECKING, Literal

import discord
from discord import app_commands
from discord.ext import commands

from utils.embeds import Embed

if TYPE_CHECKING:
    from core import Catherine


class PrideSupport(commands.Cog):
    """Commands for getting support as a person (not for this bot)"""

    def __init__(self, bot: Catherine):
        self.bot = bot

    @app_commands.command(name="pride-support")
    @app_commands.describe(support_type="The type of support your are looking for")
    @app_commands.rename(support_type="type")
    async def pride_support(
        self,
        interaction: discord.Interaction,
        support_type: Literal["HRT", "Therapy", "Hotlines", "Coming Out"],
    ) -> None:
        """Get support as a person of the LGBTQ+ community"""
        title = f"Support for {support_type}"
        description = ""
        footer = "Keep in mind to conduct your own research from reputable sources!"
        if support_type == "HRT":
            description = """
            Keep in mind that if you're a minor (-17) you will need a parental consent for Hormone Replacement Therapy (HRT)
            
            Some helpful links:
            
            NHS UK - [Link](https://www.nhs.uk/conditions/hormone-replacement-therapy-hrt/)
            Cleveland Clinic - [Link](https://my.clevelandclinic.org/health/treatments/21653-feminizing-hormone-therapy)
            Mayo Clinic - [Link](https://www.mayoclinic.org/tests-procedures/masculinizing-hormone-therapy/about/pac-20385099)
            NCBI - [Link](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5182227/)
            UCSF Transgender Care - [Link](https://transcare.ucsf.edu/hormone-therapy)
            """
        elif support_type == "Therapy":
            description = """
            Keep in mind that if you're a minor (-17) you will need a parental consent for therapy
            Some helpful links:
            
            NQTTCN - [Link](https://nqttcn.com/en/)
            Therapy For QPOC - [Link](https://www.therapyforqpoc.com/)
            Family Connections Therapy - [Link](https://familyconnectionstherapy.com/therapy-solutions/lgbtq-child-teen-therapy/)
            The Trevor Project - [Link](https://www.thetrevorproject.org/)
            """
        elif support_type == "Hotlines":
            description = """
            ```diff
            - IF YOU ARE IN A BAD SITUATION (i.e. Have already done damage to yourself) GET OFF OF DISCORD AND CALL 911
            ```
            Some helpful links:
            
            ASFP - [Link](https://afsp.org/lgbtq-crisis-and-support-resources)
            Stony Brook - [Link](https://www.stonybrook.edu/commcms/studentaffairs/lgbtq/resources/hotlines.php)
            Liam Carter - [Link](https://liamrcarter.wordpress.com/2015/09/05/list-of-lgbt-friendly-helplines-worldwide/)
            Ostem - [Link](https://ostem.org/page/crisis-hotlines)
            """
        elif support_type == "Coming Out":
            description = """
            Some helpful links:
            
            Planned Parenthood - [Link](https://www.plannedparenthood.org/learn/sexual-orientation/sexual-orientation/whats-coming-out)
            Health Line - [Link](https://www.healthline.com/health/how-to-come-out)
            Kids Health - [Link](https://kidshealth.org/en/teens/coming-out.html)
            Washington Edu - [Link](https://www.washington.edu/counseling/thinking-of-coming-out/)
            """
        embed = Embed()
        embed.title = title
        embed.description = description
        embed.set_footer(text=footer)
        await interaction.response.send_message(embed=embed)


async def setup(bot: Catherine) -> None:
    await bot.add_cog(PrideSupport(bot))
