from __future__ import annotations

from typing import TYPE_CHECKING

import asyncpg
import discord
from libs.cog_utils.commons import register_user
from libs.cog_utils.pronouns import build_approve_embed, validate_for_templating
from libs.utils import CatherineModal, CatherineView

APPROVAL_CHANNEL_ID = 1150575176006782976
NO_CONTROL_MSG = "This menu cannot be controlled by you, sorry!"

INVALID_EXAMPLE_REASON = """
It seems you tried to submit an invalid example. The example may be invalid for the following reasons:

1. The example includes one or more variables that are invalid
2. Your example contains no variables at all.

Please fix your example based on these two reasons.
"""


if TYPE_CHECKING:
    from bot.catherinecore import Catherine


# This modal is in here to avoid circular imports
class SuggestPronounsExamplesModal(CatherineModal, title="Suggest an example"):
    def __init__(
        self, interaction: discord.Interaction, bot: Catherine, pool: asyncpg.Pool
    ) -> None:
        super().__init__(
            interaction=interaction, custom_id="suggest_pronouns_example:modal"
        )
        self.sentence = discord.ui.TextInput(
            label="Sentence",
            placeholder="Enter your sentence",
            min_length=1,
            max_length=250,
            style=discord.TextStyle.long,
        )
        self.example_sentence = discord.ui.TextInput(
            label="Example Sentence",
            placeholder="Enter your example sentence with all of the correct pronouns here.",
            default=self.sentence.value,
            style=discord.TextStyle.long,
            min_length=1,
            max_length=250,
        )
        self.bot = bot
        self.pool = pool
        self.add_item(self.sentence)
        self.add_item(self.example_sentence)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        if validate_for_templating(self.sentence.value) is False:
            await interaction.response.send_message(
                INVALID_EXAMPLE_REASON, ephemeral=True
            )
            return

        query = """
        INSERT INTO pronouns_examples (sentence, user_id)
        VALUES ($2, $1)
        RETURNING id AS last_id;
        """
        async with self.pool.acquire() as conn:
            await register_user(interaction.user.id, conn)
            status = await conn.fetchval(
                query, interaction.user.id, self.sentence.value
            )
            if status is not None:
                channel = self.bot.get_channel(APPROVAL_CHANNEL_ID)
                if channel is not None and isinstance(channel, discord.TextChannel):
                    await channel.send(
                        embed=build_approve_embed(
                            self.sentence.value,
                            self.example_sentence.value,
                            interaction.user,
                        ),
                        view=ApprovePronounsExampleView(
                            self.sentence.value,
                            int(status),
                            interaction.user.id,
                            self.pool,
                        ),
                    )
                    await interaction.response.send_message(
                        "Successfully suggested sentence", ephemeral=True
                    )
                else:
                    await interaction.response.send_message(
                        "Suggestion failed due to improper setup on Noelle's end."
                    )
            else:
                await interaction.response.send_message(
                    "The sentence you are trying to suggest already exists!",
                    ephemeral=True,
                )


# This is a persistent view
# Also maybe have like a modal for reasons or something
class ApprovePronounsExampleView(discord.ui.View):
    def __init__(
        self, sentence: str, example_id: int, user_id: int, pool: asyncpg.Pool
    ):
        super().__init__(timeout=None)
        self.sentence = sentence
        self.example_id = example_id
        self.user_id = user_id
        self.pool = pool

    @discord.ui.button(
        label="Approve",
        style=discord.ButtonStyle.green,
        emoji="<:greenTick:596576670815879169>",
        custom_id="approve_pronouns_view:confirm",
    )
    async def confirm(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        query = """
        UPDATE pronouns_examples
        SET approved = $3
        WHERE id = $1 AND user_id = $2;
        """
        await self.pool.execute(query, self.example_id, self.user_id, True)
        await interaction.response.edit_message(
            content=f"Successfully approved the sentence (From: {self.user_id}, Example ID: {self.example_id})\n\nSentence: {self.sentence}",
            embed=None,
            view=None,
        )

    @discord.ui.button(
        label="Deny",
        style=discord.ButtonStyle.red,
        emoji="<:redTick:596576672149667840>",
        custom_id="approve_pronouns_view:deny",
    )
    async def deny(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        query = """
        DELETE FROM pronouns_examples
        WHERE id = $1 AND user_id = $2;
        """
        await self.pool.execute(query, self.example_id, self.user_id)
        await interaction.response.edit_message(
            content=f"Denied entry. (From: {self.user_id}, ID: {self.example_id})\n\nSentence: {self.sentence}",
            embed=None,
            view=None,
        )


class SuggestionView(CatherineView):
    def __init__(
        self, bot: Catherine, interaction: discord.Interaction, pool: asyncpg.Pool
    ):
        self.bot = bot
        self.pool = pool
        super().__init__(interaction=interaction)

    @discord.ui.button(
        label="Start",
        style=discord.ButtonStyle.green,
    )
    async def start(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        modal = SuggestPronounsExamplesModal(interaction, self.bot, self.pool)
        await interaction.response.send_modal(modal)

    @discord.ui.button(
        label="Finish",
        style=discord.ButtonStyle.green,
    )
    async def finish(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        await interaction.response.defer()
        await interaction.delete_original_response()
        self.stop()
