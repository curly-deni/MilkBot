# for discord
import nextcord
from nextcord.ext import commands
from settings import settings
from nextcord.ext import tasks

# stat count
from random import randint
from .stat_api import StatVoiceChannel

xps = {}
cookies = {}
channels = []

# for logs
import asyncio
from time import time
from datetime import datetime

# data base
import database.stat as stat
import database.serversettings as serversetting

connected = False
session = None
uri = settings["StatUri"]


def nlvl(lvl):
    if lvl != 0:
        return (5 * lvl**2 + 50 * lvl + 100) + nlvl(lvl - 1)
    else:
        return 5 * lvl**2 + 50 * lvl + 100


@tasks.loop(minutes=10)
async def addCookies():
    global cookies
    global session

    cookieso = cookies
    cookies = {}
    for server in cookieso:
        for author in cookieso[server]:
            for user in cookieso[server][author]:
                stat.addCookie(session, server, user)


@tasks.loop(seconds=30)
async def addxp():
    global xps
    global session

    xpo = xps
    xps = {}
    for server in xpo:
        for user in xpo[server]:
            stat.addXp(session, server, user, xpo[server][user])


@tasks.loop(seconds=60)  # repeat after every 60 seconds
async def reconnect():
    global session
    global connected

    connected = False
    session = stat.connectToDatabase(uri, session)
    connected = True


class StatCount(commands.Cog):
    """Discord.py based class for Stats"""

    def __init__(self, bot):
        self.bot = bot
        reconnect.start()
        addxp.start()
        addCookies.start()

    @commands.Cog.listener()
    async def on_message(self, message):
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
        global session
        global channels

        if before.channel == after.channel:
            if (
                before.self_mute == True
                or before.mute == True
                or before.self_deaf == True
                or before.deaf == True
            ):
                if (
                    after.self_mute == False
                    or after.mute == False
                    or after.self_deaf == False
                    or after.deaf == False
                ):
                    us = False
                    for c in channels:
                        if after.channel.id == c.id:
                            c.addActiveUser(member, session)
                            us = True
                    if not us:
                        channels.append(StatVoiceChannel(after.channel, session))

            if (
                before.self_mute == False
                or before.mute == False
                or before.self_deaf == False
                or before.deaf == False
            ):
                if (
                    after.self_mute == True
                    or after.mute == True
                    or after.self_deaf == True
                    or after.deaf == True
                ):
                    us = False
                    for c in channels:
                        if before.channel.id == c.id:
                            c.delActiveUser(member, session)
                            us = True

        else:
            if before.channel != None:
                us = False
                for c in channels:
                    if before.channel.id == c.id:
                        c.delActiveUser(member, session)
                        us = True
                        if len(c.activemember) == 0:
                            channels.remove(c)
            if after.channel != None:
                us = False
                for c in channels:
                    if after.channel.id == c.id:
                        c.addActiveUser(member, session)
                        us = True
                if not us:
                    channels.append(StatVoiceChannel(after.channel, session))


def setup(bot):
    bot.add_cog(StatCount(bot))
