from catherinecore import Catherine
from discord.ext import commands, ipcx


class IPCRoutes(commands.Cog):
    def __init__(self, bot: Catherine):
        self.bot = bot

    @ipcx.route()
    async def healthcheck(self, data):
        bot_status = self.bot.is_closed()
        if bot_status is True:
            return False
        return True


async def setup(bot: Catherine):
    await bot.add_cog(IPCRoutes(bot))
