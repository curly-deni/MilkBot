import nextcord
from nextcord.ext import commands
from typing import Optional
from modules.checkers import check_moderator_permission


class ReactionRoles(commands.Cog, name="Reaction Roles"):
    """Настройка сообщений для выдачи ролей по реакциям"""

    COG_EMOJI: str = "⚰️"

    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Создание")
    @commands.check(check_moderator_permission)
    @commands.guild_only()
    async def rroles_create(
        self, ctx: nextcord.ext.commands.Context, user: Optional[nextcord.Member] = None
    ):
        pass


def setup(bot):
    bot.add_cog(ReactionRoles(bot))
