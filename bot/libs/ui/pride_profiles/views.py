import asyncpg
import discord
from libs.utils import CatherineView

from .selects import SelectPrideCategory

NO_CONTROL_MSG = "This menu cannot be controlled by you, sorry!"


class ConfigureView(CatherineView):
    def __init__(self, interaction: discord.Interaction, pool: asyncpg.Pool) -> None:
        super().__init__(interaction=interaction)
        self.add_item(SelectPrideCategory(pool))

    @discord.ui.button(label="Finish", style=discord.ButtonStyle.green, row=1)
    async def finish(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        await interaction.response.defer()
        await interaction.delete_original_response()
        self.stop()
