import discord
from catherinecore import Catherine
from discord.ext import commands, tasks
from libs.cog_utils.prometheus_metrics import create_guild_gauges


class PrometheusMetrics(commands.Cog):
    """Cog which handles Prometheus metrics for Catherine-Chan"""

    def __init__(self, bot: Catherine) -> None:
        self.bot = bot
        self.metrics = self.bot.metrics

    async def cog_load(self) -> None:
        # For some reason it would only work inside here
        self.latency_loop.start()

    async def cog_unload(self) -> None:
        self.latency_loop.stop()

    @tasks.loop(seconds=5)
    async def latency_loop(self) -> None:
        self.bot.metrics.latency_gauge.labels(None).set(self.bot.latency)

    @commands.Cog.listener()
    async def on_connect(self) -> None:
        self.metrics.connection_gauge.labels(None).set(1)

    @commands.Cog.listener()
    async def on_resumed(self) -> None:
        self.metrics.connection_gauge.labels(None).set(1)

    @commands.Cog.listener()
    async def on_disconnect(self) -> None:
        self.metrics.connection_gauge.labels(None).set(0)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        create_guild_gauges(self.bot)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild) -> None:
        create_guild_gauges(self.bot)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        self.metrics.user_gauge.inc()

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member) -> None:
        self.metrics.user_gauge.dec()


async def setup(bot: Catherine) -> None:
    await bot.add_cog(PrometheusMetrics(bot))
