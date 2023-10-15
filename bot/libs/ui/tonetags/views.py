import asyncpg
import discord
from libs.cog_utils.tonetags import parse_tonetag
from libs.utils import CatherineView, ErrorEmbed, SuccessEmbed

NO_CONTROL_MSG = "This menu cannot be controlled by you, sorry!"


class DeleteToneTagView(CatherineView):
    def __init__(
        self, interaction: discord.Interaction, indicator: str, pool: asyncpg.Pool
    ) -> None:
        super().__init__(interaction=interaction)
        self.indicator = indicator
        self.pool = pool

    @discord.ui.button(
        label="Confirm",
        style=discord.ButtonStyle.green,
        emoji="<:greenTick:596576670815879169>",
    )
    async def confirm(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        parsed_tonetag = parse_tonetag(self.indicator.lower())
        query = """
        DELETE FROM tonetags
        WHERE indicator = $1 AND author_id = $2;
        """
        status = await self.pool.execute(query, parsed_tonetag, interaction.user.id)

        if status[-1] != "0":
            success_embed = SuccessEmbed()
            success_embed.description = (
                f"Successfully deleted the tonetag `{self.indicator}`"
            )
            await interaction.response.edit_message(
                embed=success_embed, delete_after=10.0, view=None
            )
        else:
            error_embed = ErrorEmbed(title="Doesn't exist")
            error_embed.description = (
                "The tonetag that you are trying to delete doesn't exist"
            )
            await interaction.response.edit_message(
                embed=error_embed, delete_after=10.0, view=None
            )

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


class DeleteToneTagViaIDView(CatherineView):
    def __init__(
        self, interaction: discord.Interaction, tonetags_id: int, pool: asyncpg.Pool
    ) -> None:
        super().__init__(interaction=interaction)
        self.tonetags_id = tonetags_id
        self.pool = pool

    @discord.ui.button(
        label="Confirm",
        style=discord.ButtonStyle.green,
        emoji="<:greenTick:596576670815879169>",
    )
    async def confirm(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        query = """
        DELETE FROM tonetags
        WHERE id = $1 AND author_id = $2;
        """
        status = await self.pool.execute(query, self.tonetags_id, interaction.user.id)

        if status[-1] != "0":
            success_embed = SuccessEmbed()
            success_embed.description = (
                f"Successfully deleted the tonetag. (ID: `{self.tonetags_id}`)"
            )
            await interaction.response.edit_message(
                embed=success_embed, delete_after=10.0, view=None
            )
        else:
            error_embed = ErrorEmbed(title="Doesn't exist")
            error_embed.description = f"You either have the wrong ID (ID: `{self.tonetags_id}`) or the tonetag does not exist. Also maybe it's that you can't delete that tonetag."
            await interaction.response.edit_message(
                embed=error_embed, delete_after=10.0, view=None
            )

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
