# for discord
import nextcord
from nextcord.ext import commands, tasks
from nextcord.utils import get
from settings import adminRoles, settings

# for logs
import asyncio
from time import time
from datetime import datetime

# database
import database.moderation as moderation
from database.serversettings import getAdminRole

connected = False
session = None
uri = settings["StatUri"]

from database.db_classes import getTextMutesClass, getVoiceMutesClass
from additional.check_permission import check_permission


@tasks.loop(seconds=30)
async def reconnect():
    global session
    global connected

    connected = False
    session = moderation.connectToDatabase(uri, session)
    connected = True


class Moderation(commands.Cog, name="Модерация"):
    """Модерация с помощью MilkBot"""

    COG_EMOJI = "👮"

    def __init__(self, bot):
        self.bot = bot
        reconnect.start()
        self.checkMutes.start()

    # check database for ended mutes
    @tasks.loop(seconds=10)
    async def checkMutes(self):
        global session
        global connected

        for x in self.bot.guilds:
            if not connected:
                await asyncio.sleep(1)

            role = get(x.roles, name="Muted")

            # get enspired mutes
            try:
                texts = moderation.getTextMutes(session, x.id)
                voices = moderation.getVoiceMutes(session, x.id)

                # check voice mutes
                for e in texts:
                    user = await x.fetch_member(e.uid)
                    await user.remove_roles(role)
                    moderation.delTextElement(session, x.id, e)
                    await user.send("Текстовый мут снят!")

                # check voice mutes list
                for e in voices:
                    user = await x.fetch_member(e.uid)

                    # if user in voice
                    try:
                        await user.edit(mute=False)
                        moderation.delVoiceElement(session, x.id, e)
                        await user.send("Голосовой мут снят!")

                    # if not: still in mutes
                    except:
                        pass
            except:
                pass

    @commands.command(pass_content=True, brief="Временный тексовый мут")
    async def тмут(self, ctx, *параметры):
        global connected
        global session

        args = параметры

        adminroles = getAdminRole(session, ctx.guild.id)
        for x in ctx.author.roles:
            if adminroles != None:
                if str(x.id) in adminroles:

                    delayx = 0
                    time_start = datetime.now()

                    if args != ():
                        # if not connected to database
                        if connected != True:
                            await asyncio.sleep(1)

                        # if user mentioned, message content if format <@user uid>
                        usr = args[0]
                        if usr.startswith("<"):
                            usr = usr[3:-1]

                        # get member class
                        try:
                            user = await ctx.guild.fetch_member(usr)
                            pass
                        except:
                            await ctx.send("Неверный ввод UID!")

                        # generate time
                        args = list(args)
                        args.pop(0)
                        removex = []
                        for x in args:
                            if x.find("d") != -1:
                                e = x[:-1]
                                delayx += int(e) * 86400
                                removex.append(x)
                            elif x.find("h") != -1:
                                e = x[:-1]
                                delayx += int(e) * 3600
                                removex.append(x)
                            elif x.find("m") != -1:
                                e = x[:-1]
                                delayx += int(e) * 60
                                removex.append(x)
                        for x in removex:
                            args.remove(x)

                        time_stop = datetime.fromtimestamp(
                            time_start.timestamp() + delayx
                        )

                        reason = (" ").join(args)

                        x = getTextMutesClass(ctx.guild.id)
                        x.uid = user.id
                        x.time_start = time_start
                        x.time_stop = time_stop
                        x.created = ctx.author.id
                        x.reason = reason

                        emb = generateEmbed(x, user, ctx.author)
                        x.__tablename__ = f"{x.__tablename__}-{ctx.guild.id}"

                        try:
                            moderation.addTextMutes(session, x)
                        except:
                            return
                        role = get(ctx.guild.roles, name="Muted")
                        await user.add_roles(role)
                        await ctx.send(embed=emb)
                        await user.send(embed=emb)
                        return
                    else:
                        await ctx.send(
                            "тмут <uid/упоминание> <время (1d 2h 3m)> <причина>"
                        )
                        return

    @commands.command(pass_content=True, brief="Временный голосовой мут")
    async def вмут(self, ctx, *параметры):
        global connected
        global session

        args = параметры

        adminroles = serversettings.getAdminRole(session, ctx.guild.id)
        if check_permission(ctx.author.roles, adminroles):

            delayx = 0
            time_start = datetime.now()

            if args != ():
                # if not connected to database
                if connected != True:
                    await asyncio.sleep(1)

                # if user mentioned, message content if format <@user uid>
                usr = args[0]
                if usr.startswith("<"):
                    usr = usr[3:-1]

                # get member class
                try:
                    user = await ctx.guild.fetch_member(usr)
                    pass
                except:
                    await ctx.send("Неверный ввод UID!")

                # generate time
                args = list(args)
                args.pop(0)
                removex = []
                for x in args:
                    if x.find("d") != -1:
                        e = x[:-1]
                        delayx += int(e) * 86400
                        removex.append(x)
                    elif x.find("h") != -1:
                        e = x[:-1]
                        delayx += int(e) * 3600
                        removex.append(x)
                    elif x.find("m") != -1:
                        e = x[:-1]
                        delayx += int(e) * 60
                        removex.append(x)
                for x in removex:
                    args.remove(x)

                reason = (" ").join(args)
                time_stop = datetime.fromtimestamp(time_start.timestamp() + delayx)
                x = getVoiceMutesClass(guildid)

                x.uid = user.id
                x.time_start = time_start
                x.time_stop = time_stop
                x.created = ctx.author.id
                x.reason = reason

                emb = generateEmbed(x, user, ctx.author)

                try:
                    moderation.addVoiceMutes(session, x)

                except:
                    return

                await user.edit(mute=True)
                await ctx.send(embed=emb)
                await user.send(embed=emb)
            else:
                await ctx.send("m!вмут <uid/упоминание> <время (1d 2h 3m)> <причина>")


def generateEmbed(x, user, author):
    if x.__tablename__.find("textmute") != -1:
        emb = nextcord.Embed(title=f"Выдан мут для текстовых каналов!")

    else:
        emb = nextcord.Embed(title=f"Выдан мут для голосовых каналов!")

    emb.set_thumbnail(
        url="https://raw.githubusercontent.com/I-dan-mi-I/images/main/mute.png"
    )
    emb.add_field(name="Замьюченный", value=user, inline=False)
    emb.add_field(name="Выдал", value=author, inline=False)
    emb.add_field(
        name="Время начала",
        value=x.time_start.strftime("%d-%m-%Y %H:%M:%S"),
        inline=True,
    )
    emb.add_field(
        name="Время конца", value=x.time_stop.strftime("%d-%m-%Y %H:%M:%S"), inline=True
    )
    emb.add_field(name="Причина", value=x.reason, inline=False)
    return emb


def setup(bot):
    bot.add_cog(Moderation(bot))
