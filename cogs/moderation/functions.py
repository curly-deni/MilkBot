# for nextcord
import nextcord
from nextcord.ext import commands, tasks
from nextcord.ext.commands import Context
from nextcord.utils import get
from modules.checkers import check_moderator_permission


def seals_check(ctx: Context) -> bool:
    return ctx.message.guild.id in [876474448126050394, 938461972448559116]


class Moderation(commands.Cog, name="Модерация"):
    """Модерация с помощью MilkBot"""

    COG_EMOJI: str = "👮"

    def __init__(self, bot):
        self.bot = bot
        if self.bot.bot_type != "helper":
            self.check_mutes.start()

    async def cog_check(self, ctx: Context) -> bool:
        return check_moderator_permission(ctx)

    # check database for ended mutes
    @tasks.loop(seconds=10)
    async def check_mutes(self):

        for guild in self.bot.guilds:
            role: nextcord.Role = get(guild.roles, name="Muted")

            try:
                texts: list = self.bot.database.get_expired_text_mutes(guild.id)
                voices = self.bot.database.get_expired_voice_mutes(guild.id)

                # check voice mutes
                for member in texts:
                    user: nextcord.Member = await guild.fetch_member(member.id)
                    try:
                        await user.remove_roles(role)
                        self.bot.database.del_text_mute(member.id, guild.id)
                    except:
                        continue

                # check voice mutes list
                for member in voices:
                    user: nextcord.Member = await guild.fetch_member(member.id)
                    try:
                        await user.edit(mute=False)
                        self.bot.database.del_voice_mute(member.id, guild.id)
                    except:
                        continue
            except:
                continue


def setup(bot):
    bot.add_cog(Moderation(bot))
