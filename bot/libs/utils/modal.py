import traceback

import discord
from discord.utils import utcnow

from .embeds import ErrorEmbed, FullErrorEmbed

NO_CONTROL_MSG = "This modal cannot be controlled by you, sorry!"


def produce_error_embed(error: Exception) -> ErrorEmbed:
    error_traceback = "\n".join(traceback.format_exception_only(type(error), error))
    embed = ErrorEmbed()
    embed.description = f"""
    Uh oh! It seems like the modal ran into an issue! For support, please visit [Catherine-Chan's Support Server](https://discord.gg/ns3e74frqn) to get help!
    
    **Error**:
    ```{error_traceback}```
    """
    embed.set_footer(text="Happened At")
    embed.timestamp = utcnow()
    return embed


class CatherineModal(discord.ui.Modal):
    def __init__(self, interaction: discord.Interaction, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.interaction = interaction

    async def interaction_check(self, interaction: discord.Interaction, /) -> bool:
        if interaction.user and interaction.user.id in (
            self.interaction.client.application.owner.id,  # type: ignore
            self.interaction.user.id,
        ):
            return True
        await interaction.response.send_message(NO_CONTROL_MSG, ephemeral=True)
        return False

    async def on_error(
        self, interaction: discord.Interaction, error: Exception, /
    ) -> None:
        await interaction.response.send_message(
            embed=FullErrorEmbed(error), ephemeral=True
        )
        self.stop()
