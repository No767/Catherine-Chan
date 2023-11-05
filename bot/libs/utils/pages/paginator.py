from __future__ import annotations

from typing import Any, Dict, Optional

import discord
from discord.ext import menus

from .modals import NumberedPageModal


# This is originally from RoboDanny's Paginator class (RoboPages)
# This one is actually adapted for compatibility with interactions, which is Akari's version of this
class CatherinePages(discord.ui.View):
    def __init__(
        self,
        source: menus.PageSource,
        *,
        interaction: discord.Interaction,
        check_embeds: bool = True,
        compact: bool = False,
    ):
        super().__init__()
        self.source: menus.PageSource = source
        self.check_embeds: bool = check_embeds
        self.interaction: discord.Interaction = interaction
        self.followup: Optional[discord.InteractionMessage] = None
        self.current_page: int = 0
        self.compact: bool = compact
        self.clear_items()
        self.fill_items()

    def fill_items(self) -> None:
        if not self.compact:
            self.numbered_page.row = 1
            self.stop_pages.row = 1

        if self.source.is_paginating():
            max_pages = self.source.get_max_pages()
            use_last_and_first = max_pages is not None and max_pages >= 2
            if use_last_and_first:
                self.add_item(self.go_to_first_page)
            self.add_item(self.go_to_previous_page)
            if not self.compact:
                self.add_item(self.go_to_current_page)
            self.add_item(self.go_to_next_page)
            if use_last_and_first:
                self.add_item(self.go_to_last_page)
            if not self.compact:
                self.add_item(self.numbered_page)
            self.add_item(self.stop_pages)

    async def _get_kwargs_from_page(self, page: int) -> Dict[str, Any]:
        value = await discord.utils.maybe_coroutine(self.source.format_page, self, page)
        if isinstance(value, dict):
            return value
        elif isinstance(value, str):
            return {"content": value, "embed": None}
        elif isinstance(value, discord.Embed):
            return {"embed": value, "content": None}
        else:
            return {}

    async def show_page(
        self, interaction: discord.Interaction, page_number: int
    ) -> None:
        page = await self.source.get_page(page_number)
        self.current_page = page_number
        kwargs = await self._get_kwargs_from_page(page)
        self._update_labels(page_number)
        if kwargs:
            if interaction.response.is_done():
                if self.followup:
                    await self.followup.edit(**kwargs, view=self)
            else:
                await interaction.response.edit_message(**kwargs, view=self)

    def _update_labels(self, page_number: int) -> None:
        self.go_to_first_page.disabled = page_number == 0
        if self.compact:
            max_pages = self.source.get_max_pages()
            self.go_to_last_page.disabled = (
                max_pages is None or (page_number + 1) >= max_pages
            )
            self.go_to_next_page.disabled = (
                max_pages is not None and (page_number + 1) >= max_pages
            )
            self.go_to_previous_page.disabled = page_number == 0
            return

        self.go_to_current_page.label = str(page_number + 1)
        self.go_to_previous_page.label = str(page_number)
        self.go_to_next_page.label = str(page_number + 2)
        self.go_to_next_page.disabled = False
        self.go_to_previous_page.disabled = False
        self.go_to_first_page.disabled = False

        max_pages = self.source.get_max_pages()
        if max_pages is not None:
            self.go_to_last_page.disabled = (page_number + 1) >= max_pages
            if (page_number + 1) >= max_pages:
                self.go_to_next_page.disabled = True
                self.go_to_next_page.label = "…"
            if page_number == 0:
                self.go_to_previous_page.disabled = True
                self.go_to_previous_page.label = "…"

    async def show_checked_page(
        self, interaction: discord.Interaction, page_number: int
    ) -> None:
        max_pages = self.source.get_max_pages()
        try:
            if max_pages is None:
                # If it doesn't give maximum pages, it cannot be checked
                await self.show_page(interaction, page_number)
            elif max_pages > page_number >= 0:
                await self.show_page(interaction, page_number)
        except IndexError:
            # An error happened that can be handled, so ignore it.
            pass

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user and interaction.user.id in (
            self.interaction.client.application.owner.id,  # type: ignore
            self.interaction.user.id,
        ):
            return True
        await interaction.response.send_message(
            "This pagination menu cannot be controlled by you, sorry!", ephemeral=True
        )
        return False

    async def on_timeout(self) -> None:
        if self.followup and self.interaction.response.is_done():
            await self.interaction.edit_original_response(view=None)

    async def on_error(
        self, interaction: discord.Interaction, error: Exception, item: discord.ui.Item
    ) -> None:
        await interaction.followup.send(
            "An unknown error occurred, sorry", ephemeral=True
        )

    async def start(
        self, *, content: Optional[str] = None, ephemeral: bool = False
    ) -> None:
        if self.check_embeds and not self.interaction.permissions.embed_links:
            await self.interaction.response.send_message(
                "Bot doesn't have embed link perms in this channel", ephemeral=True
            )
            return

        await self.source._prepare_once()
        page = await self.source.get_page(0)
        kwargs = await self._get_kwargs_from_page(page)
        if content:
            kwargs.setdefault("content", content)

        self._update_labels(0)

        # Fixes the issue of somehow the interaction failing for /pronouns profile
        if self.interaction.response.is_done():
            await self.interaction.followup.send(
                **kwargs, view=self, ephemeral=ephemeral
            )
            self.followup = await self.interaction.original_response()
            return

        await self.interaction.response.send_message(
            **kwargs, view=self, ephemeral=ephemeral
        )
        self.followup = await self.interaction.original_response()

    @discord.ui.button(label="≪", style=discord.ButtonStyle.grey)
    async def go_to_first_page(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """go to the first page"""
        await self.show_page(interaction, 0)

    @discord.ui.button(label="Back", style=discord.ButtonStyle.blurple)
    async def go_to_previous_page(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """go to the previous page"""
        await self.show_checked_page(interaction, self.current_page - 1)

    # Shows the current button
    @discord.ui.button(label="Current", style=discord.ButtonStyle.grey, disabled=True)
    async def go_to_current_page(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """show current page"""

    @discord.ui.button(label="Next", style=discord.ButtonStyle.blurple)
    async def go_to_next_page(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """go to the next page"""
        await self.show_checked_page(interaction, self.current_page + 1)

    @discord.ui.button(label="≫", style=discord.ButtonStyle.grey)
    async def go_to_last_page(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """go to the last page"""
        # The call here is safe because it's guarded by skip_if
        await self.show_page(interaction, self.source.get_max_pages() - 1)  # type: ignore

    @discord.ui.button(label="Skip to page...", style=discord.ButtonStyle.grey)
    async def numbered_page(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """lets you type a page number to go to"""
        if self.followup is None:
            return

        modal = NumberedPageModal(self.source.get_max_pages())
        await interaction.response.send_modal(modal)
        timed_out = await modal.wait()

        if timed_out:
            await interaction.followup.send("Took too long", ephemeral=True)
            return
        elif self.is_finished():
            await modal.interaction.response.send_message(
                "Took too long", ephemeral=True
            )
            return

        value = str(modal.page.value)
        if not value.isdigit():
            await modal.interaction.response.send_message(
                f"Expected a number not {value!r}", ephemeral=True
            )
            return

        value = int(value)
        await self.show_checked_page(modal.interaction, value - 1)
        if not modal.interaction.response.is_done():
            error = modal.page.placeholder.replace("Enter", "Expected")  # type: ignore # Can't be None
            await modal.interaction.response.send_message(error, ephemeral=True)

    @discord.ui.button(label="Quit", style=discord.ButtonStyle.red)
    async def stop_pages(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """stops the pagination session."""
        await interaction.response.defer()
        await interaction.delete_original_response()
        self.stop()
