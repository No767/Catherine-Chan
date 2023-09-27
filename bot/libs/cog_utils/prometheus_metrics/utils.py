from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import app_commands
from prometheus_client import Counter, Gauge

from .structs import GuildMetrics, Metrics

if TYPE_CHECKING:
    from bot.catherinecore import Catherine

METRIC_PREFIX = "discord_"


def get_stats(bot: Catherine) -> GuildMetrics:
    # The same way R. Danny does it
    total_commands = 0
    total_members = 0
    total_unique = len(bot.users)
    text = 0
    voice = 0
    guilds = 0
    for guild in bot.guilds:
        guilds += 1
        if guild.unavailable:
            continue
        total_members += guild.member_count or 0
        for channel in guild.channels:
            if isinstance(channel, discord.TextChannel):
                text += 1
            elif isinstance(channel, discord.VoiceChannel):
                voice += 1

    for cmd in bot.tree.walk_commands():
        if isinstance(cmd, app_commands.commands.Command):
            total_commands += 1

    return GuildMetrics(
        text=text,
        voice=voice,
        guilds=guilds,
        total_members=total_members,
        total_unique_members=total_unique,
        total_commands=total_commands,
    )


def create_gauges() -> Metrics:
    return Metrics(
        connection_gauge=Gauge(
            f"{METRIC_PREFIX}connected",
            "Determines if the bot is connected to Discord",
            ["shard"],
        ),
        latency_gauge=Gauge(
            f"{METRIC_PREFIX}latency",
            "latency to Discord",
            ["shard"],
        ),
        on_app_command_counter=Counter(
            f"{METRIC_PREFIX}on_app_command",
            "Amount of slash commands called by users",
        ),
        guild_gauge=Gauge(
            f"{METRIC_PREFIX}stat_total_guilds",
            "Amount of guilds this bot is in",
        ),
        text_channel_gauge=Gauge(
            f"{METRIC_PREFIX}stat_total_text_channels",
            "Amount of text channels this bot is has access to",
        ),
        voice_channel_gauge=Gauge(
            f"{METRIC_PREFIX}stat_total_voice_channels",
            "Amount of voice channels this bot is has access to",
        ),
        user_gauge=Gauge(
            f"{METRIC_PREFIX}stat_total_users", "Amount of users this bot can see"
        ),
        user_unique_gauge=Gauge(
            f"{METRIC_PREFIX}stat_total_unique_users",
            "Amount of unique users this bot can see",
        ),
        commands_gauge=Gauge(
            f"{METRIC_PREFIX}stat_app_total_commands", "Amount of commands"
        ),
    )


def create_guild_gauges(bot: Catherine):
    stats = get_stats(bot)
    bot_metrics = bot.metrics

    bot_metrics.guild_gauge.set(stats.guilds)
    bot_metrics.text_channel_gauge.set(stats.text)
    bot_metrics.voice_channel_gauge.set(stats.voice)
    bot_metrics.user_gauge.set(stats.total_members)
    bot_metrics.user_unique_gauge.set(stats.total_unique_members)


def fill_gauges(bot: Catherine):
    stats = get_stats(bot)
    bot_metrics = bot.metrics

    bot_metrics.commands_gauge.set(stats.total_commands)
    bot_metrics.on_app_command_counter.inc(0)

    if bot.is_closed():
        bot_metrics.connection_gauge.labels(None).set(0)
        return

    bot_metrics.connection_gauge.labels(None).set(1)
