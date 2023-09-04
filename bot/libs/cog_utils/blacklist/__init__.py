import discord
from discord import app_commands


async def check_is_owner(interaction: discord.Interaction):
    return await interaction.client.is_owner(interaction.user)  # type: ignore # lying...


def is_owner():
    async def pred(interaction: discord.Interaction) -> bool:
        return await check_is_owner(interaction)

    return app_commands.check(pred)
