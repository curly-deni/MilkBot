# This is COG of MilkBot part functions

# for discord
import nextcord
from nextcord.ext import commands
from nextcord.utils import get
from nextcord.ext import tasks
from settings import settings
from settings import adminRoles

# database
connected = False
session = None
uri = settings["StatUri"]
import database.voicechannels as voicechannels
import database.voicesettings as voicesettings
from database.moderation import addVoiceMutes
from database.db_classes import getVoiceMutesClass
import database.serversettings as serversettings

# for log
import asyncio
from time import time
from datetime import datetime

from additional.check_permission import isAdmin


@tasks.loop(seconds=30)
async def reconnect():
    global session
    global connected

    connected = False
    session = voicechannels.connectToDatabase(uri, session)
    connected = True


class Voice(commands.Cog, name="Приватные голосовые каналы"):
    """Создание и настройка приватных голосовых каналов"""

    COG_EMOJI = "📞"

    def __init__(self, bot):
        self.count = 0
        self.bot = bot
        reconnect.start()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        global session
        global connected

        if not connected:
            await asyncio.sleep(1)

        ss = serversettings.getInfo(session, member.guild.id)
        if ss == "not setup":
            return False

        PrivateVoice = ss.voicegenerator
        PrivateCategory = ss.voicecategory
        UserRoles = ss.userroles.split(",")
        AdminRoles = ss.adminroles.split(",")

        if before.channel != None and after.channel != None:
            if before.channel.id == after.channel.id:
                return False

        try:
            checkInGenerator = after.channel.id == PrivateVoice
            checkInPrivate = (
                after.channel.category.id == PrivateCategory
                and after.channel.id != PrivateVoice
            )
            pass
        except:
            checkInGenerator = False
            checkInPrivate = False
            pass

        try:
            checkOutPrivate = (
                before.channel.category.id == PrivateCategory
                and before.channel.id != PrivateVoice
            )
            pass
        except:
            checkOutPrivate = False
            pass

        if checkInGenerator:
            await self.create_new_channel(
                member, PrivateCategory, UserRoles, AdminRoles
            )

        if checkInPrivate:
            await self.InPrivate(member, after)

        if checkOutPrivate:
            await self.OutPrivate(member, before)

    @commands.command(brief="Кик пользователя")
    @commands.guild_only()
    async def войс_кик(self, ctx, member=None):
        try:
            await ctx.message.delete()
            pass
        except nextcord.errors.Forbidden:
            pass

        if member == None:
            e = "войс_кик (упоминание пользователя)"
        else:
            member = ctx.message.mentions[0]

            ss = serversettings.getInfo(session, ctx.guild.id)

            if isAdmin(member.roles, ss.adminroles):
                return

            if ctx.author.voice != None:

                if ctx.author.voice.channel.permissions_for(ctx.author).manage_channels:
                    if member.voice != None:
                        try:
                            await member.move_to(None)
                            e = "Успешно выгнан!"
                            pass
                        except Exception as el:
                            e = f"При изгнании произошла ошибка: {el}"
                            pass

                    else:
                        e = "Объект не находится в голосовом канале!"

                else:
                    e = "Вы находитесь не в своём голосовом канале!"

            else:
                e = "Вы не находитесь в голосовом канале!"

        await ctx.send(e, delete_after=10)

    @commands.command(brief="Мут пользователя")
    @commands.guild_only()
    async def войс_мут(self, ctx, member=None):
        try:
            await ctx.message.delete()
            pass
        except nextcord.errors.Forbidden:
            pass

        if member == None:
            e = "войс_мут (упоминание пользователя)"
        else:
            member = ctx.message.mentions[0]

            ss = serversettings.getInfo(session, ctx.guild.id)

            if isAdmin(member.roles, ss.adminroles):
                return

            if ctx.author.voice != None:
                if ctx.author.voice.channel.permissions_for(ctx.author).manage_channels:
                    if member.voice != None:
                        if ctx.author.voice.channel.permissions_for(member).speak:
                            try:
                                overwrite = nextcord.PermissionOverwrite(speak=False)
                                await member.edit(mute=True)
                                await ctx.author.voice.channel.set_permissions(
                                    member, overwrite=overwrite
                                )
                                e = "Успешно замучен!"

                                if not connected:
                                    await asyncio.sleep(1)

                                voicesettings.addMuted(
                                    session, ctx.guild.id, ctx.author.id, member.id
                                )
                                pass
                            except Exception as el:
                                e = f"При муте произошла ошибка: {el}"
                                pass
                        else:
                            try:
                                await member.edit(mute=False)
                                await ctx.author.voice.channel.set_permissions(
                                    member, overwrite=None
                                )
                                e = "Успешно размучен!"

                                if not connected:
                                    await asyncio.sleep(1)

                                voicesettings.delMuted(
                                    session, ctx.guild.id, ctx.author.id, member.id
                                )
                                pass
                            except Exception as el:
                                e = f"При размуте произошла ошибка: {el}"
                                pass

                    else:
                        e = "Объект не находится в голосовом канале!"

                else:
                    e = "Вы находитесь не в своём голосовом канале!"

            else:
                e = "Вы не находитесь в голосовом канале!"

        await ctx.send(content=e, delete_after=10)

    @commands.command(brief="Бан пользователя")
    @commands.guild_only()
    async def войс_бан(self, ctx, member=None):
        try:
            await ctx.message.delete()
            pass
        except nextcord.errors.Forbidden:
            pass

        if member == None:
            e = "войс_бан (упоминание пользователя)"
        else:
            member = ctx.message.mentions[0]

            ss = serversettings.getInfo(session, ctx.guild.id)

            if isAdmin(member.roles, ss.adminroles):
                return

            if ctx.author.voice != None:

                if ctx.author.voice.channel.permissions_for(ctx.author).manage_channels:
                    if ctx.author.voice.channel.permissions_for(member).connect:
                        try:
                            overwrite = nextcord.PermissionOverwrite(connect=False)
                            await member.move_to(None)
                            await ctx.author.voice.channel.set_permissions(
                                member, overwrite=overwrite
                            )
                            e = "Успешно забанен!"

                            if not connected:
                                await asyncio.sleep(1)

                            voicesettings.addBanned(
                                session, ctx.guild.id, ctx.author.id, member.id
                            )
                            pass
                        except Exception as el:
                            e = f"При бане произошла ошибка: {el}"
                            pass
                    else:
                        try:
                            await ctx.author.voice.channel.set_permissions(
                                member, overwrite=None
                            )
                            e = "Успешно разбанен!"

                            if not connected:
                                await asyncio.sleep(1)

                            voicesettings.delBanned(
                                session, ctx.guild.id, ctx.author.id, member.id
                            )
                            pass
                        except Exception as el:
                            e = f"При разбане произошла ошибка: {el}"
                            pass

                else:
                    e = "Вы находитесь не в своём голосовом канале!"

            else:
                e = "Вы не находитесь в голосовом канале!"

        await ctx.send(e, delete_after=10)

    @commands.command(aliases=["войс_имя"], brief="Смена названия канала")
    @commands.guild_only()
    async def войс_название(self, ctx, *, name=None):
        try:
            await ctx.message.delete()
            pass
        except nextcord.errors.Forbidden:
            pass

        if name == None:
            e = "войс_название (название канала)"
        else:

            if ctx.author.voice != None:

                if ctx.author.voice.channel.permissions_for(ctx.author).manage_channels:

                    global session
                    global connected

                    if not connected:
                        await asyncio.sleep(1)

                    try:
                        await ctx.author.voice.channel.edit(name=name)
                        voicesettings.setName(
                            session, ctx.guild.id, ctx.author.id, name
                        )
                        e = "Успешно изменено!"
                    except Exception as el:
                        e = f"При изменении канала произошла ошибка: {el}"

                else:
                    e = "Вы находитесь не в своём голосовом канале!"

            else:
                e = "Вы не находитесь в голосовом канале!"

        await ctx.send(e, delete_after=10)

    @commands.command(brief="Смена битрейта канала")
    @commands.guild_only()
    async def войс_битрейт(self, ctx, bitrate=None):
        try:
            await ctx.message.delete()
            pass
        except nextcord.errors.Forbidden:
            pass

        if bitrate == None:
            e = "войс_битрейт (битрейт)"
        else:
            try:
                bitrate = int(bitrate)
            except:
                await ctx.send("Укажите число")
            if ctx.author.voice != None:

                if ctx.author.voice.channel.permissions_for(ctx.author).manage_channels:

                    global session
                    global connected

                    if not connected:
                        await asyncio.sleep(1)

                    try:
                        await ctx.author.voice.channel.edit(bitrate=bitrate * 1000)
                        voicesettings.setBitrate(
                            session, ctx.guild.id, ctx.author.id, bitrate * 1000
                        )
                        e = "Успешно изменено!"
                    except Exception as el:
                        e = f"При изменении канала произошла ошибка: {el}"

                else:
                    e = "Вы находитесь не в своём голосовом канале!"

            else:
                e = "Вы не находитесь в голосовом канале!"

        await ctx.send(e, delete_after=10)

    @commands.command(brief="Ограничить максимальное число пользователей")
    @commands.guild_only()
    async def войс_макс(self, ctx, max=None):
        try:
            await ctx.message.delete()
            pass
        except nextcord.errors.Forbidden:
            pass

        if max == None:
            e = "войс_макс (максимальное число пользователей)"
        else:
            if ctx.author.voice != None:

                if ctx.author.voice.channel.permissions_for(ctx.author).manage_channels:

                    global session
                    global connected

                    if not connected:
                        await asyncio.sleep(1)

                    try:
                        await ctx.author.voice.channel.edit(user_limit=max)
                        voicesettings.setMaxUser(
                            session, ctx.guild.id, ctx.author.id, max
                        )
                        e = "Успешно изменено!"
                    except Exception as el:
                        e = f"При изменении канала произошла ошибка: {el}"

                else:
                    e = "Вы находитесь не в своём голосовом канале!"

            else:
                e = "Вы не находитесь в голосовом канале!"

        await ctx.send(e, delete_after=10)

    @commands.command(brief="Открыть канал")
    @commands.guild_only()
    async def войс_открыть(self, ctx):
        try:
            await ctx.message.delete()
            pass
        except nextcord.errors.Forbidden:
            pass

        if ctx.author.voice != None:

            if ctx.author.voice.channel.permissions_for(ctx.author).manage_channels:

                global session
                global connected

                if not connected:
                    await asyncio.sleep(1)

                ss = serversettings.getInfo(session, ctx.guild.id)
                if ss == "not setup":
                    return False

                UserRoles = ss.userroles.split(",")

                usroles = []
                for user in UserRoles:
                    if user != "":
                        usroles.append(get(ctx.author.guild.roles, id=int(user)))

                if ctx.author.voice.channel.overwrites_for(usroles[0]).connect:
                    try:
                        for role in usroles:
                            await ctx.author.voice.channel.set_permissions(
                                role, connect=False
                            )
                        voicesettings.setOpen(
                            session, ctx.guild.id, ctx.author.id, False
                        )
                        e = "Успешно закрыт!"
                    except Exception as el:
                        e = f"При изменении канала произошла ошибка: {el}"

                else:
                    try:
                        for role in usroles:
                            await ctx.author.voice.channel.set_permissions(
                                role, connect=True
                            )
                        voicesettings.setOpen(
                            session, ctx.guild.id, ctx.author.id, True
                        )
                        e = "Успешно открыт!"
                    except Exception as el:
                        e = f"При изменении канала произошла ошибка: {el}"

            else:
                e = "Вы находитесь не в своём голосовом канале!"

        else:
            e = "Вы не находитесь в голосовом канале!"

        await ctx.send(e, delete_after=10)

    @commands.command(brief="Скрыть канал от участников сервера")
    @commands.guild_only()
    async def войс_скрыть(self, ctx):
        try:
            await ctx.message.delete()
            pass
        except nextcord.errors.Forbidden:
            pass

        if ctx.author.voice != None:

            if ctx.author.voice.channel.permissions_for(ctx.author).manage_channels:

                global session
                global connected

                if not connected:
                    await asyncio.sleep(1)

                ss = serversettings.getInfo(session, ctx.guild.id)
                if ss == "not setup":
                    return False

                UserRoles = ss.userroles.split(",")

                usroles = []
                for user in UserRoles:
                    if user != "":
                        usroles.append(get(ctx.author.guild.roles, id=int(user)))

                if ctx.author.voice.channel.overwrites_for(usroles[0]).connect:
                    try:
                        for role in usroles:
                            await ctx.author.voice.channel.set_permissions(
                                role, view_channel=False
                            )
                        voicesettings.setVisible(
                            session, ctx.guild.id, ctx.author.id, False
                        )
                        e = "Успешно скрыт!"
                    except Exception as el:
                        e = f"При изменении канала произошла ошибка: {el}"

                else:
                    try:
                        for role in usroles:
                            await ctx.author.voice.channel.set_permissions(
                                role, view_channel=True
                            )
                        voicesettings.setVisible(
                            session, ctx.guild.id, ctx.author.id, True
                        )
                        e = "Успешно раскрыт!"
                    except Exception as el:
                        e = f"При изменении канала произошла ошибка: {el}"

            else:
                e = "Вы находитесь не в своём голосовом канале!"

        else:
            e = "Вы не находитесь в голосовом канале!"

        await ctx.send(e, delete_after=10)

    @commands.command(brief="Создание прикреплённого текстового канала")
    @commands.guild_only()
    async def войс_текст(self, ctx):
        try:
            await ctx.message.delete()
            pass
        except nextcord.errors.Forbidden:
            pass

        if ctx.author.voice != None:
            if ctx.author.voice.channel.permissions_for(ctx.author).manage_channels:

                global session
                global connected

                if not connected:
                    await asyncio.sleep(1)

                ss = serversettings.getInfo(session, ctx.guild.id)
                if ss == "not setup":
                    return False

                xa = voicechannels.getInfo(
                    session, ctx.guild.id, ctx.author.voice.channel.id
                )
                xb = voicesettings.getInfo(session, ctx.guild.id, ctx.author.id)
                if not xb.text or xa.txuid == None:
                    if ctx.author.voice.channel.category.id == ss.voicecategory:
                        category = get(ctx.guild.categories, id=ss.voicecategory)

                        TextChannel = await category.create_text_channel(name=xb.name)

                        voicechannels.addTextChannelByUID(
                            session,
                            ctx.guild.id,
                            ctx.author.voice.channel.id,
                            TextChannel.id,
                        )
                        voicesettings.setText(
                            session, ctx.guild.id, ctx.author.id, True
                        )

                        UserRoles = ss.userroles.split(",")
                        AdminRoles = ss.adminroles.split(",")

                        usroles = []
                        adroles = []
                        for user in UserRoles:
                            if user != "":
                                usroles.append(get(member.guild.roles, id=int(user)))
                        for admin in AdminRoles:
                            if admin != "":
                                adroles.append(get(member.guild.roles, id=int(admin)))

                        try:
                            for role in usroles:
                                await TextChannel.set_permissions(
                                    role,
                                    view_channel=True,
                                    read_messages=False,
                                    read_message_history=False,
                                    send_messages=False,
                                )

                            for role in adroles:
                                await TextChannel.set_permissions(
                                    role,
                                    view_channel=True,
                                    manage_channels=True,
                                    read_messages=True,
                                    read_message_history=True,
                                    send_messages=True,
                                )
                        except:
                            pass

                        e = "Успешно создан!"

                else:
                    textuid = None
                    if xa.txuid != None and xa.txuid != "":
                        textuid = xa.txuid

                    if textuid != None:
                        TextChannel = ctx.guild.get_channel(textuid)
                        await TextChannel.delete()
                        voicesettings.setText(
                            session, ctx.guild.id, ctx.author.id, False
                        )
                        voicechannels.addTextChannelByUID(
                            session, ctx.guild.id, ctx.author.voice.channel.id, None
                        )

                    e = "Успешно удалён!"

            else:
                e = "Вы находитесь не в своём голосовом канале!"

        else:
            e = "Вы не находитесь в голосовом канале!"

        await ctx.send(e, delete_after=10)

    @commands.command(brief="Открыть канал для")
    @commands.guild_only()
    async def войс_открыть_для(self, ctx, member=None):
        try:
            await ctx.message.delete()
            pass
        except nextcord.errors.Forbidden:
            pass

        if member == None:
            e = "войс_открыть_для (упоминание пользователя)"
        else:

            if ctx.author.voice != None:

                if ctx.author.voice.channel.permissions_for(ctx.author).manage_channels:

                    global session
                    global connected

                    if not connected:
                        await asyncio.sleep(1)

                    ss = serversettings.getInfo(session, ctx.guild.id)
                    if ss == "not setup":
                        return False

                    if isAdmin(member.roles, ss.adminroles):
                        return

                    if ctx.author.voice.channel.permissions_for(member).view_channel:
                        try:
                            await ctx.author.voice.channel.set_permissions(
                                member, view_channel=False
                            )
                            voicesettings.addMuted(
                                session, ctx.guild.id, ctx.author.id, member.id
                            )
                            e = f"Успешно скрыт для {member.name}!"
                        except Exception as el:
                            e = f"При изменении канала произошла ошибка: {el}"

                    else:
                        try:
                            await ctx.author.voice.channel.set_permissions(
                                member, view_channel=True
                            )
                            voicesettings.delMuted(
                                session, ctx.guild.id, ctx.author.id, member.id
                            )
                            e = f"Успешно раскрыт для {member.name}!"
                        except Exception as el:
                            e = f"При изменении канала произошла ошибка: {el}"

                else:
                    e = "Вы находитесь не в своём голосовом канале!"

            else:
                e = "Вы не находитесь в голосовом канале!"

        await ctx.send(e, delete_after=10)

    async def create_new_channel(self, member, PrivateCategory, UserRoles, AdminRoles):
        global session
        global connected

        category = get(member.guild.categories, id=PrivateCategory)

        # create voice channel
        if not connected:
            await asyncio.sleep(1)

        xe = voicesettings.getInfo(session, member.guild.id, member.id)
        if xe.name == None or xe.name == "":
            name = member.name
        else:
            name = xe.name

        bitrate = xe.bitrate

        if xe.maxuser == None:
            maxuser = 0
        else:
            maxuser = xe.maxuser

        VoiceChannel = await category.create_voice_channel(
            name=name, bitrate=bitrate, user_limit=maxuser
        )
        usroles = []
        adroles = []
        for user in UserRoles:
            if user != "":
                usroles.append(get(member.guild.roles, id=int(user)))
        for admin in AdminRoles:
            if admin != "":
                adroles.append(get(member.guild.roles, id=int(admin)))

        if xe.text != None:
            text = xe.text
        else:
            text = False

        if xe.banned != None:
            g = xe.banned.split(",")
            banned_ar = []

            for usr in g:
                try:
                    banned_ar.append(await member.guild.fetch_member(usr))
                    pass
                except:
                    pass

            for usr in banned_ar:
                await VoiceChannel.set_permissions(usr, connect=False)

        if xe.opened != None:
            g = xe.opened.split(",")
            opened_ar = []

            for usr in g:
                try:
                    opened_ar.append(await member.guild.fetch_member(usr))
                    pass
                except:
                    pass

            for usr in opened_ar:
                await VoiceChannel.set_permissions(usr, connect=True, view_channel=True)

        if xe.muted != None:
            g = xe.muted.split(",")
            muted_ar = []

            for usr in g:
                try:
                    muted_ar.append(await member.guild.fetch_member(int(usr)))
                    pass
                except:
                    pass

            for usr in muted_ar:
                await VoiceChannel.set_permissions(usr, speak=False)

        if xe.open != None:
            openx = xe.open
        else:
            openx = True

        if xe.visible != None:
            visiblex = xe.visible
        else:
            visiblex = True

        if not openx or not visiblex:

            if not xe.open:
                for role in usroles:
                    await VoiceChannel.set_permissions(
                        role, connect=False, view_channel=True
                    )

            if not xe.visible:
                for role in usroles:
                    await VoiceChannel.set_permissions(role, view_channel=False)

        else:
            for role in usroles:
                await VoiceChannel.set_permissions(
                    role, connect=True, view_channel=True
                )

        await VoiceChannel.set_permissions(
            member, manage_channels=True, connect=True, speak=True, view_channel=True
        )
        await VoiceChannel.set_permissions(
            member, manage_channels=True, connect=True, speak=True, view_channel=True
        )
        await VoiceChannel.set_permissions(
            member, manage_channels=True, connect=True, speak=True, view_channel=True
        )

        for role in adroles:
            await VoiceChannel.set_permissions(
                role,
                manage_channels=True,
                connect=True,
                speak=True,
                view_channel=True,
                kick_members=True,
                mute_members=True,
            )

        # create text_channel
        if text:
            TextChannel = await category.create_text_channel(name=name)

            await TextChannel.set_permissions(
                member,
                view_channel=True,
                manage_channels=True,
                read_messages=True,
                read_message_history=True,
                send_messages=True,
            )

            for role in usroles:

                await TextChannel.set_permissions(
                    role,
                    view_channel=True,
                    read_messages=False,
                    read_message_history=False,
                    send_messages=False,
                )

            for role in adroles:
                await TextChannel.set_permissions(
                    role,
                    view_channel=True,
                    manage_channels=True,
                    read_messages=True,
                    read_message_history=True,
                    send_messages=True,
                )

            voicechannels.addInfo(
                session, member.guild.id, VoiceChannel.id, TextChannel.id, member.id
            )
        else:
            voicechannels.addInfo(
                session, member.guild.id, VoiceChannel.id, None, member.id
            )

        await member.move_to(VoiceChannel)

    async def InPrivate(self, member, after):
        global connected
        global session

        if not connected:
            await asyncio.sleep(1)

        TextChannelUID = voicechannels.getTextChannelByUID(
            session, member.guild.id, after.channel.id
        )
        if TextChannelUID is not None:
            TextChannel = member.guild.get_channel(TextChannelUID)
            try:
                await TextChannel.set_permissions(
                    member,
                    view_channel=True,
                    read_messages=True,
                    read_message_history=True,
                    send_messages=True,
                )
            except:
                pass

    async def OutPrivate(self, member, before):
        global connected
        global session

        try:
            await member.edit(mute=False)
            pass
        except:
            if not connected:
                await asyncio.sleep(1)

            if not before.channel.permissions_for(member).speak:
                addVoiceMutes(
                    session,
                    getVoiceMutesClass(member.guild.id)(
                        uid=member.id,
                        time_start=datetime.now(),
                        time_stop=datetime.now(),
                        reason="private channel mute",
                        created=1234,
                    ),
                )
            pass

        if len(before.channel.members) == 0:
            xe = voicechannels.getInfo(
                session, before.channel.guild.id, before.channel.id
            )
            textuid = None
            if xe != None:
                textuid = xe.txuid
                voicechannels.delChannel(session, before.channel.guild.id, xe)
            await before.channel.delete()

            if textuid != None:
                try:
                    TextChannel = member.guild.get_channel(textuid)
                    await TextChannel.delete()
                except:
                    pass

        else:
            xe = voicechannels.getInfo(
                session, before.channel.guild.id, before.channel.id
            )
            textuid = None
            if xe != None:
                textuid = xe.txuid

            if textuid != None:
                TextChannel = member.guild.get_channel(textuid)
                await TextChannel.set_permissions(
                    member,
                    view_channel=True,
                    read_messages=False,
                    read_message_history=False,
                    send_messages=False,
                )


def setup(bot):
    bot.add_cog(Voice(bot))
