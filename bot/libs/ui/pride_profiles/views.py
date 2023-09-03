import asyncpg
import discord
from libs.cog_utils.commons import register_user
from libs.utils import ErrorEmbed, SuccessEmbed

from .selects import SelectPrideCategory

NO_CONTROL_MSG = "This menu cannot be controlled by you, sorry!"


class ConfirmRegisterView(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, pool: asyncpg.Pool) -> None:
        super().__init__()
        self.interaction = interaction
        self.pool = pool

    # The RDanny styled interaction check
    async def interaction_check(self, interaction: discord.Interaction, /):
        if interaction.user and interaction.user.id in (
            self.interaction.client.application.owner.id,  # type: ignore
            self.interaction.user.id,
        ):
            return True
        await interaction.response.send_message(NO_CONTROL_MSG, ephemeral=True)
        return False

    @discord.ui.button(
        label="Confirm",
        style=discord.ButtonStyle.green,
        emoji="<:greenTick:596576670815879169>",
    )
    async def confirm(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        query = """
        INSERT INTO profiles (user_id, name)
        VALUES ($1, $2)
        ON CONFLICT (user_id) DO NOTHING;
        """

        async with self.pool.acquire() as conn:
            await register_user(interaction.user.id, conn)
            status = await conn.execute(
                query, interaction.user.id, interaction.user.global_name
            )

            if status[-1] != "0":
                success_embed = SuccessEmbed()
                success_embed.description = "Registered your pride profile!"
                await interaction.response.edit_message(
                    embed=success_embed, delete_after=10.0, view=None
                )
            else:
                error_embed = ErrorEmbed(title="Already registered")
                error_embed.description = "You already have a pride profile registered!"
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


class ConfigureView(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, pool: asyncpg.Pool) -> None:
        super().__init__()
        self.add_item(SelectPrideCategory(pool))
        self.interaction = interaction

    async def interaction_check(self, interaction: discord.Interaction, /):
        if interaction.user and interaction.user.id in (
            self.interaction.client.application.owner.id,  # type: ignore
            self.interaction.user.id,
        ):
            return True
        await interaction.response.send_message(NO_CONTROL_MSG, ephemeral=True)
        return False

    @discord.ui.button(label="Finish", style=discord.ButtonStyle.green, row=1)
    async def finish(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        await interaction.response.defer()
        await interaction.delete_original_response()
        self.stop()


class DeleteProfileView(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, pool: asyncpg.Pool) -> None:
        super().__init__()
        self.interaction = interaction
        self.pool = pool

    async def interaction_check(self, interaction: discord.Interaction, /):
        if interaction.user and interaction.user.id in (
            self.interaction.client.application.owner.id,  # type: ignore
            self.interaction.user.id,
        ):
            return True
        await interaction.response.send_message(NO_CONTROL_MSG, ephemeral=True)
        return False

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

        if status[-1] != "0":
            success_embed = SuccessEmbed()
            success_embed.description = "Successfully deleted your pride profile"
            await interaction.response.edit_message(
                embed=success_embed, delete_after=10.0, view=None
            )
        else:
            error_embed = ErrorEmbed(title="Doesn't exist")
            error_embed.description = (
                "The pride profile that you are trying to delete doesn't exist"
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