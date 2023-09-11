from typing import Literal

import discord
from catherinecore import Catherine
from discord import app_commands
from discord.ext import commands
from libs.utils import Embed


# Yep making it better Jade
class Support(commands.Cog):
    """Commands for getting support as a person (not for this bot)"""

    def __init__(self, bot: Catherine):
        self.bot = bot

    @app_commands.command(name="pride-server")
    async def pride_servers(self, interaction: discord.Interaction) -> None:
        """Get a list of LGBTQ oriented discord servers"""
        embed = Embed()
        embed.title = "Servers for LGBTQ+"
        embed.description = """
        ***This bot is not affiliated or associated with these servers at all!***
        
        LGTBTQ+ Hangout - https://www.discord.gg/Pride
        Transcord - https://discord.gg/trans
        The LGBTQ+ Community - https://discord.gg/pridemonth
        Enby_eautiful - https://discord.gg/j8MCnEC64S
        """
        embed.set_footer(
            text="If you are enjoying Catherine-Chan, please consider to tell your friends about this bot! If you can't, then you can still show your support by upvoting on Top.gg!",
            icon_url="https://cdn.discordapp.com/emojis/1096897624432443392.webp?size=128&quality=lossless",
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="support")
    @app_commands.describe(type="The type of support your are looking for")
    async def support(
        self,
        interaction: discord.Interaction,
        type: Literal["HRT", "Therapy", "Hotlines", "Coming Out"],
    ) -> None:
        """Get support as a person of the LGBTQ+ community"""
        title = f"Support for {type}"
        description = ""
        if type == "HRT":
            description = """
            Keep in mind that if you're a minor (-17) you will need a parental consent for Hormone Replacement Therapy (HRT)
            
            Some helpful links:
            
            NHS UK - [Link](https://www.nhs.uk/conditions/hormone-replacement-therapy-hrt/)
            Cleveland Clinic - [Link](https://my.clevelandclinic.org/health/treatments/21653-feminizing-hormone-therapy)
            Mayo Clinic - [Link](https://www.mayoclinic.org/tests-procedures/masculinizing-hormone-therapy/about/pac-20385099)
            NCBI - [Link](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5182227/)
            """
        elif type == "Therapy":
            description = """
            Keep in mind that if you're a minor (-17) you will need a parental consent for therapy
            Some helpful links:
            
            NQTTCN - [Link](https://nqttcn.com/en/)
            Therapy For QPOC - [Link](https://www.therapyforqpoc.com/)
            Family Connections Therapy - [Link](https://familyconnectionstherapy.com/therapy-solutions/lgbtq-child-teen-therapy/)
            The Trevor Project - [Link](https://www.thetrevorproject.org/)
            """
        elif type == "Hotlines":
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
        elif type == "Coming Out":
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
        await interaction.response.send_message(embed=embed)


async def setup(bot: Catherine) -> None:
    await bot.add_cog(Support(bot))
