import nextcord
from nextcord.ext import commands
from modules.checkers import check_moderator_permission


class FakeAstral(commands.Cog, name="Астрал"):
    """Стратегическая игра Астрал."""

    COG_EMOJI: str = "🌰"

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        brief="Список текущих игровых сессий Астрала с возможностью остановки"
    )
    @commands.check(check_moderator_permission)
    @commands.guild_only()
    async def астрал_стоп(
        self, ctx: nextcord.ext.commands.Context, game_uuid: str = ""
    ):
        pass

    @commands.command(brief="Старт игры с ботом")
    @commands.guild_only()
    async def астрал_бот(self, ctx):
        pass

    @commands.command(brief="Старт игры с боссом")
    @commands.guild_only()
    async def астрал_босс(self, ctx):
        pass

    @commands.command(brief="Старт игры")
    @commands.guild_only()
    async def астрал_старт(self, ctx):
        pass


def setup(bot):
    bot.add_cog(FakeAstral(bot))
