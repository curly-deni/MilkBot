# for discord
from nextcord.ext import commands, tasks
from nextcord.ext.commands import Context

# stat count
from random import randint
from .stat_api import StatVoiceChannel

xps = {}
cookies = {}
channels = []


def nlvl(lvl):
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

        cookieso = cookies
        cookies = {}
        for server in cookieso:
            for author in cookieso[server]:
                for user in cookieso[server][author]:
                    self.bot.database.add_cookie(user, server, 1)

    @tasks.loop(seconds=30)
    async def add_xp(self):
        global xps

        xpo = xps
        xps = {}
        for server in xpo:
            for user in xpo[server]:
                self.bot.database.add_xp(user, server, xpo[server][user])

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            if message.content.find("🍪") != -1:
                if len(message.mentions) == 1:
                    try:
                        g = cookies[message.guild.id]
                    except:
                        cookies[message.guild.id] = {}
                        pass

                    try:
                        a = cookies[message.guild.id][message.author.id]
                    except:
                        cookies[message.guild.id][message.author.id] = {}
                        pass

                    try:
                        u = cookies[message.guild.id][message.author.id][
                            message.mentions[0].id
                        ]
                    except:
                        cookies[message.guild.id][message.author.id][
                            message.mentions[0].id
                        ] = 1
                        return

            try:
                g = xps[message.guild.id]
            except:
                xps[message.guild.id] = {}
                xp = randint(15, 25)
                xps[message.guild.id][message.author.id] = xp
                return

            try:
                o = g[message.author.id]
            except:
                xp = randint(15, 25)
                xps[message.guild.id][message.author.id] = xp
                return

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):

        global channels

        if before.channel == after.channel:
            if before.self_mute or before.mute or before.self_deaf or before.deaf:
                if (
                    not after.self_mute
                    or not after.mute
                    or not after.self_deaf
                    or not after.deaf
                ):
                    us = False
                    for c in channels:
                        if after.channel.id == c.id:
                            c.add_active_user(member)
                            us = True
                    if not us:
                        channels.append(StatVoiceChannel(after.channel, self.bot))

            if (
                not before.self_mute
                or not before.mute
                or not before.self_deaf
                or not before.deaf
            ):
                if after.self_mute or after.mute or after.self_deaf or after.deaf:
                    us = False
                    for c in channels:
                        if before.channel.id == c.id:
                            c.del_active_user(member)
                            us = True

        else:
            if before.channel is not None:
                us = False
                for c in channels:
                    if before.channel.id == c.id:
                        c.del_active_user(member)
                        us = True
                        if len(c.activemember) == 0:
                            channels.remove(c)
            if after.channel is not None:
                us = False
                for c in channels:
                    if after.channel.id == c.id:
                        c.add_active_user(member)
                        us = True
                if not us:
                    channels.append(StatVoiceChannel(after.channel, self.bot))


def setup(bot):
    bot.add_cog(StatCount(bot))
