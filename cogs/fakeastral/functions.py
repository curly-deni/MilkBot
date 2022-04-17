# for nextcord
import asyncio

import nextcord
from nextcord.ext import commands
from async_timeout import timeout
from additional.check_permission import check_admin_permissions


class FakeAstral(commands.Cog, name="Астрал"):
    """Стратегическая игра Астрал."""

    COG_EMOJI = "🌰"

    def __init__(self, bot):
        self.bot = bot
        self.games = {}

    @commands.command(brief="Остановка игры администратором")
    @commands.check(check_admin_permissions)
    @commands.guild_only()
    async def астрал_стоп(self, ctx):
        pass

    @commands.command(pass_content=True, brief="Старт игры с ботом")
    @commands.guild_only()
    async def астрал_бот(self, ctx):
        pass

    @commands.command(pass_content=True, brief="Старт игры с боссом")
    @commands.guild_only()
    async def астрал_босс(self, ctx):
        pass

    @commands.command(pass_content=True, brief="Старт игры")
    @commands.guild_only()
    async def астрал_старт(self, ctx):
        pass


def setup(bot):
    bot.add_cog(FakeAstral(bot))
