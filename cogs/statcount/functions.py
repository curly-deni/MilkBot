# for discord
import nextcord
from nextcord.ext import commands, tasks
from nextcord.ext.commands import Context
from nextcord.utils import get
from typing import Union

# stat count
from random import randint
from .stat_api import StatVoiceChannel

xps: dict = {}
cookies: dict = {}
channels: list[StatVoiceChannel] = []


def nlvl(lvl: int) -> int:
    if lvl != 0:
        return (5 * lvl**2 + 50 * lvl + 100) + nlvl(lvl - 1)
    else:
        return 5 * lvl**2 + 50 * lvl + 100


class StatCount(commands.Cog):
    """Discord.py based class for Stats"""

    def __init__(self, bot):
        self.bot = bot

        self.add_xp.start()
        self.add_cookies.start()

    def cog_check(self, ctx: Context) -> bool:
        return ctx.message.guild.id != 876474448126050394

    @tasks.loop(minutes=10)
    async def add_cookies(self):
        global cookies

        cookies_old = cookies.copy()
        cookies = {}
        for server in cookies_old:
            for author in cookies_old[server]:
                for user in cookies_old[server][author]:
                    self.bot.database.add_cookie(user, server, 1)

    @tasks.loop(seconds=30)
    async def add_xp(self):
        global xps

        xp_old = xps.copy()
        xps = {}
        for server in xp_old:
            for user in xp_old[server]:
                self.bot.database.add_xp(user, server, xp_old[server][user])

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        if not message.author.bot:
            if message.content.find("🍪") != -1:
                if message.mentions:
                    if message.guild.id in cookies:
                        return
                    else:
                        cookies[message.guild.id]: dict = {}

                    if message.author.id in cookies[message.guild.id]:
                        return
                    else:
                        cookies[message.guild.id][message.author.id]: dict = {}

                    for mentioned_member in message.mentions:
                        if (
                            mentioned_member.id
                            not in cookies[message.guild.id][message.author.id]
                        ):
                            cookies[message.guild.id][message.author.id][
                                mentioned_member.id
                            ] = 1

            if message.guild.id not in xps:
                xps[message.guild.id]: dict = {}
                xps[message.guild.id][message.author.id]: int = randint(15, 25)
                return
            else:
                if message.author.id not in xps[message.guild.id]:
                    xps[message.guild.id][message.author.id]: int = randint(15, 25)
                    return

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: nextcord.Member,
        before: nextcord.VoiceState,
        after: nextcord.VoiceState,
    ):

        global channels

        if before.channel == after.channel:
            if before.self_mute or before.mute or before.self_deaf or before.deaf:
                if (
                    not after.self_mute
                    or not after.mute
                    or not after.self_deaf
                    or not after.deaf
                ):
                    channel: Union[StatVoiceChannel, None] = get(
                        channels, id=after.channel.id
                    )
                    if channel is not None:
                        channel.add_active_user(member)
                    else:
                        channels.append(StatVoiceChannel(after.channel, self.bot))

            if (
                not before.self_mute
                or not before.mute
                or not before.self_deaf
                or not before.deaf
            ):
                if after.self_mute or after.mute or after.self_deaf or after.deaf:
                    channel: Union[StatVoiceChannel, None] = get(
                        channels, id=before.channel.id
                    )
                    if channel is not None:
                        channel.del_active_user(member)

        else:
            if before.channel is not None:
                channel: Union[StatVoiceChannel, None] = get(
                    channels, id=before.channel.id
                )
                if channel is not None:
                    channel.del_active_user(member)
                    if len(channel.activemember) == 0:
                        channels.remove(channel)
            if after.channel is not None:
                channel: Union[StatVoiceChannel, None] = get(
                    channels, id=after.channel.id
                )
                if channel is not None:
                    channel.add_active_user(member)
                else:
                    channels.append(StatVoiceChannel(after.channel, self.bot))


def setup(bot):
    bot.add_cog(StatCount(bot))
