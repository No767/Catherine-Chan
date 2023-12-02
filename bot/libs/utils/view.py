import traceback
from typing import Any, Optional

import discord
from discord.utils import utcnow

from .embeds import ErrorEmbed

NO_CONTROL_MSG = "This view cannot be controlled by you, sorry!"


def make_error_embed(error: Exception, item: discord.ui.Item[Any]) -> ErrorEmbed:
    error_traceback = "\n".join(traceback.format_exception_only(type(error), error))
    embed = ErrorEmbed()
    embed.description = f"""
    Uh oh! It seems like the view ran into an issue! For support, please visit [Catherine-Chan's Support Server](https://discord.gg/ns3e74frqn) to get help!
    
    **Item**: `{item.__class__.__name__}`
    
    **Error**:
    ```{error_traceback}```
    """
    embed.set_footer(text="Happened At")
    embed.timestamp = utcnow()
    return embed


class CatherineView(discord.ui.View):
    def __init__(
        self,
        interaction: discord.Interaction,
        message_after: bool = True,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.interaction = interaction
        self.message_after = message_after
        self.original_response: Optional[discord.InteractionMessage]

    async def interaction_check(self, interaction: discord.Interaction, /) -> bool:
        if interaction.user and interaction.user.id in (
            self.interaction.client.application.owner.id,  # type: ignore
            self.interaction.user.id,
        ):
            return True
        await interaction.response.send_message(NO_CONTROL_MSG, ephemeral=True)
        return False

    async def on_timeout(self) -> None:
        if self.original_response:
            if self.message_after:
                embed = ErrorEmbed()
                embed.title = "\U00002757 Timed Out"
                embed.description = (
                    "Timed out waiting for a response. Cancelling action."
                )
                await self.original_response.edit(
                    embed=embed, view=None, delete_after=15.0
                )
                return

            await self.original_response.edit(view=None)

    async def on_error(
        self,
        interaction: discord.Interaction,
        error: Exception,
        item: discord.ui.Item[Any],
        /,
    ) -> None:
        await interaction.response.send_message(
            embed=make_error_embed(error, item), ephemeral=True
        )
        self.stop()
