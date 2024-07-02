import asyncpg
import discord
from libs.utils import CatherineView
from libs.utils.embeds import ErrorEmbed, SuccessEmbed, TimeoutEmbed

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


class DeleteProfileView(CatherineView):
    def __init__(self, interaction: discord.Interaction, pool: asyncpg.Pool) -> None:
        super().__init__(interaction=interaction)
        self.pool = pool

    def build_register_embed(self, status: str) -> discord.Embed:
        if status[-1] == "0":
            error_embed = ErrorEmbed()
            error_embed.title = "Doesn't Exist"
            error_embed.description = (
                "The pride profile that you are trying to delete doesn't exist"
            )
            return error_embed

        success_embed = SuccessEmbed()
        success_embed.description = "Successfully deleted your pride profile"
        return success_embed

    async def on_timeout(self) -> None:
        if self.original_response and not self.triggered.is_set():
            await self.original_response.edit(
                embed=TimeoutEmbed(), view=None, delete_after=15.0
            )

    @discord.ui.button(
        label="Confirm",
        style=discord.ButtonStyle.green,
        emoji="<:greenTick:596576670815879169>",
    )
    async def confirm(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        query = """
        DELETE FROM profiles
        WHERE user_id = $1;
        """
        status = await self.pool.execute(query, interaction.user.id)
        embed = self.build_register_embed(status)
        if self.original_response:
            self.triggered.set()
            await self.original_response.edit(embed=embed, view=None, delete_after=15.0)

    @discord.ui.button(
        label="Cancel",
        style=discord.ButtonStyle.red,
        emoji="<:redTick:596576672149667840>",
    )
    async def cancel(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        await interaction.response.defer()
        await interaction.delete_original_response()
        self.stop()
