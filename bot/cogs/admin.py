from __future__ import annotations

import asyncio
import importlib
import os
import re
import subprocess  # nosec # We already know this is dangerous, but it's needed
import sys
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncIterator,
    List,
    Literal,
    Optional,
    Tuple,
    TypeVar,
    Union,
)

import discord
from discord.ext import commands, menus
from libs.utils.pages.paginator import CatherineContextPages

if TYPE_CHECKING:
    from catherinecore import Catherine

# Although this regex does introduce polynomial backtracing, there is simply
# no other alternatives as this is used for a partial search
# Simply the only other choice is to leave it as is,
# since i have continue to attempt to fix it, i'm simply wasting my own time
# (the marginal cost is off the roof for this one)
GIT_PULL_REGEX = re.compile(r"\s+(?P<filename>.*)\b\s+\|\s+[\d]")
NO_CONTROL_MSG = "This view cannot be controlled by you, sorry!"

_T = TypeVar("_T")


class BlacklistPageSource(menus.AsyncIteratorPageSource):
    def __init__(self, entries: dict[str, Union[_T, Any]]):
        super().__init__(self.blacklist_iterator(entries), per_page=20)

    async def blacklist_iterator(self, entries: dict[str, Union[_T, Any]]) -> AsyncIterator[str]:
        for key, entry in entries.items():
            yield f"{key}: {entry}"

    async def format_page(self, menu, entries: list[str]) -> discord.Embed:
        pages = []
        for index, entry in enumerate(entries, start=menu.current_page * self.per_page):
            pages.append(f"{index + 1}. {entry}")

        menu.embed.description = "\n".join(pages)
        return menu.embed


class BlacklistPages(CatherineContextPages):
    def __init__(self, entries: dict[str, Union[_T, Any]], *, ctx: commands.Context):
        super().__init__(BlacklistPageSource(entries), ctx=ctx)
        self.embed = discord.Embed(colour=discord.Colour.from_rgb(200, 168, 255))


# This is not a subclassed view as we need to use ctx for the implementation,
# not interactions
class ConfirmationView(discord.ui.View):
    def __init__(self, ctx: commands.Context, timeout: float, delete_after: bool):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.value: Optional[bool] = None
        self.delete_after = delete_after
        self.message: Optional[discord.Message] = None

    async def on_timeout(self) -> None:
        if self.delete_after and self.message:
            await self.message.delete()
        elif self.message:
            await self.message.edit(view=None)

    async def interaction_check(self, interaction: discord.Interaction, /) -> bool:
        if interaction.user and interaction.user.id in (
            self.ctx.bot.application.owner.id,
            self.ctx.author.id,
        ):
            return True

        await interaction.response.send_message(NO_CONTROL_MSG, ephemeral=True)
        return False

    async def delete_response(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if self.delete_after:
            await interaction.delete_original_response()

        self.stop()

    @discord.ui.button(
        label="Confirm",
        style=discord.ButtonStyle.green,
        emoji="<:greenTick:596576670815879169>",
    )
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        self.value = True
        if self.delete_after:
            await self.delete_response(interaction)

    @discord.ui.button(
        label="Cancel",
        style=discord.ButtonStyle.red,
        emoji="<:redTick:596576672149667840>",
    )
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        self.value = False
        await self.delete_response(interaction)


class Admin(commands.Cog, command_attrs=dict(hidden=True)):
    """Administrative cog to handle admin tasks"""

    def __init__(self, bot: Catherine) -> None:
        self.bot = bot

    async def cog_check(self, ctx: commands.Context) -> bool:
        return await self.bot.is_owner(ctx.author)

    async def reload_or_load_extension(self, module: str) -> None:
        try:
            await self.bot.reload_extension(module)
        except commands.ExtensionNotLoaded:
            await self.bot.load_extension(module)

    def find_modules_from_git(self, output: str) -> List[Tuple[int, str]]:
        files = GIT_PULL_REGEX.findall(output)
        ret: list[tuple[int, str]] = []
        for file in files:
            root, ext = os.path.splitext(file)
            if ext != ".py" or root.endswith("__init__"):
                continue

            true_root = ".".join(root.split("/")[1:])

            if true_root.startswith("cogs") or true_root.startswith("libs"):
                # A subdirectory within these are a part of the codebase

                ret.append((true_root.count(".") + 1, true_root))

        # For reload order, the submodules should be reloaded first
        ret.sort(reverse=True)
        return ret

    async def run_process(self, command: str) -> List[str]:
        process = await asyncio.create_subprocess_shell(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        result = await process.communicate()

        return [output.decode() for output in result]

    def tick(self, opt: Optional[bool], label: Optional[str] = None) -> str:
        lookup = {
            True: "\U00002705",
            False: "\U0000274c",
            None: "\U000023e9",
        }
        emoji = lookup.get(opt, "\U0000274c")
        if label is not None:
            return f"{emoji}: {label}"
        return emoji

    def format_results(self, statuses: List) -> str:
        desc = (
            "\U00002705 - Successful reload | \U0000274c - Failed reload | \U000023e9 - Skipped\n\n"
        )
        status = "\n".join(f"- {status}: `{module}`" for status, module in statuses)
        desc += status
        return desc

    async def reload_exts(self, module: str) -> List[Tuple[str, str]]:
        statuses = []
        try:
            await self.reload_or_load_extension(module)
            statuses.append((self.tick(True), module))
        except commands.ExtensionError:
            statuses.append((self.tick(False), module))

        return statuses

    def reload_lib_modules(self, module: str) -> List[Tuple[str, str]]:
        statuses = []
        try:
            actual_module = sys.modules[module]
            importlib.reload(actual_module)
            statuses.append((self.tick(True), module))
        except KeyError:
            statuses.append((self.tick(None), module))
        except Exception:
            statuses.append((self.tick(False), module))
        return statuses

    async def prompt(
        self,
        ctx: commands.Context,
        message: str,
        *,
        timeout: float = 60.0,
        delete_after: bool = True,
    ) -> Optional[bool]:
        view = ConfirmationView(ctx, timeout=timeout, delete_after=delete_after)
        view.message = await ctx.send(message, view=view, ephemeral=delete_after)
        await view.wait()
        return view.value

    @commands.guild_only()
    @commands.command(name="sync", hidden=True)
    async def sync(
        self,
        ctx: commands.Context,
        guilds: commands.Greedy[discord.Object],
        spec: Optional[Literal["~", "*", "^"]] = None,
    ) -> None:
        """Performs a sync of the tree. This will sync, copy globally, or clear the tree."""
        await ctx.defer()
        if not guilds:
            if spec == "~":
                synced = await self.bot.tree.sync(guild=ctx.guild)
            elif spec == "*":
                self.bot.tree.copy_global_to(guild=ctx.guild)  # type: ignore
                synced = await self.bot.tree.sync(guild=ctx.guild)
            elif spec == "^":
                self.bot.tree.clear_commands(guild=ctx.guild)
                await self.bot.tree.sync(guild=ctx.guild)
                synced = []
            else:
                synced = await self.bot.tree.sync()

            await ctx.send(
                f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
            )
            return

        ret = 0
        for guild in guilds:
            try:
                await self.bot.tree.sync(guild=guild)
            except discord.HTTPException:
                pass
            else:
                ret += 1

        await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")

    @commands.command(name="reload-all", hidden=True)
    async def reload(self, ctx: commands.Context) -> None:
        """Reloads all cogs and utils"""
        async with ctx.typing():
            stdout, _ = await self.run_process("git pull")

        # progress and stuff is redirected to stderr in git pull
        # however, things like "fast forward" and files
        # along with the text "already up-to-date" are in stdout

        if stdout.startswith("Already up-to-date."):
            await ctx.send(stdout)
            return

        modules = self.find_modules_from_git(stdout)

        mods_text = "\n".join(
            f"{index}. `{module}`" for index, (_, module) in enumerate(modules, start=1)
        )
        prompt_text = f"This will update the following modules, are you sure?\n{mods_text}"

        confirm = await self.prompt(ctx, prompt_text)
        if not confirm:
            await ctx.send("Aborting....")
            return

        statuses = []
        for is_submodule, module in modules:
            if is_submodule:
                statuses = self.reload_lib_modules(module)
            else:
                statuses = await self.reload_exts(module)

        await ctx.send(self.format_results(statuses))

    @commands.guild_only()
    @commands.group(name="blacklist", invoke_without_command=True)
    async def blacklist(self, ctx: commands.Context) -> None:
        """Global blacklisting system - Without subcommand you are viewing the blacklist"""
        entries = self.bot.blacklist.all()
        if len(entries) == 0:
            await ctx.send("No blacklist entries found")
            return

        pages = BlacklistPages(entries, ctx=ctx)
        await pages.start()

    @blacklist.command(name="add")
    async def add(self, ctx: commands.Context, id: discord.Object):
        """Adds an ID to the global blacklist"""
        given_id = id.id
        await self.bot.add_to_blacklist(given_id)
        self.bot.metrics.blacklist.users.inc()
        await ctx.send(f"Done. Added ID {given_id} to the blacklist")

    @blacklist.command(name="remove")
    async def remove(self, ctx: commands.Context, id: discord.Object):
        """Removes an ID from the global blacklist"""
        given_id = id.id
        await self.bot.remove_from_blacklist(given_id)
        self.bot.metrics.blacklist.users.dec()
        await ctx.send(f"Done. Removed ID {given_id} from the blacklist")


async def setup(bot: Catherine) -> None:
    await bot.add_cog(Admin(bot))
