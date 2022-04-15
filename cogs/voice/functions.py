import nextcord
from nextcord.ext import commands, tasks
from nextcord.utils import get
from settings import settings, adminRoles
from additional.check_permission import isAdmin

# database


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

# buttons
from .actions import ControlButtons


class Voice(commands.Cog, name="Приватные голосовые каналы"):
    """Создание и настройка приватных голосовых каналов"""

    COG_EMOJI = "📞"

    def __init__(self, bot):
        self.count = 0
        self.bot = bot

    @commands.command(brief="Обновить сообщение")
    @commands.guild_only()
    async def войс_сообщение(self, ctx):

        if ctx.author.voice is not None:

            if ctx.author.voice.channel.permissions_for(ctx.author).manage_channels:

                message_id = voicechannels.getSettingsMessageUID(
                    self.bot.databaseSession, ctx.guild.id, ctx.author.voice.channel.id
                )
                channel_id = voicechannels.getTextChannelByUID(
                    self.bot.databaseSession, ctx.guild.id, ctx.author.voice.channel.id
                )

                channel = self.bot.get_channel(channel_id)
                message: nextcord.Message = await channel.fetch_message(message_id)

                buttons = ControlButtons(self.bot)

                await message.edit(message.content, embeds=message.embeds, view=buttons)
                await buttons.wait()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):

        ss = serversettings.getInfo(self.bot.databaseSession, member.guild.id)
        if ss == "not setup":
            return False

        PrivateVoice = ss.voicegenerator
        PrivateCategory = ss.voicecategory
        UserRoles = ss.userroles.split(",")
        AdminRoles = ss.adminroles.split(",")

        if before.channel is not None and after.channel is not None:
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

        if checkInPrivate:
            await self.InPrivate(member, after)

        if checkOutPrivate:
            await self.OutPrivate(member, before)

        if checkInGenerator:
            await self.create_new_channel(
                member, PrivateCategory, UserRoles, AdminRoles
            )

    async def create_new_channel(self, member, PrivateCategory, UserRoles, AdminRoles):

        category = get(member.guild.categories, id=PrivateCategory)

        # create voice channel

        xe = voicesettings.getInfo(self.bot.databaseSession, member.guild.id, member.id)
        if xe.name is None or xe.name == "":
            name = member.name
        else:
            name = xe.name

        bitrate = xe.bitrate

        if xe.maxuser is None:
            maxuser = 0
        else:
            maxuser = xe.maxuser

        VoiceChannel = await category.create_voice_channel(
            name=name, bitrate=bitrate, user_limit=maxuser
        )

        await VoiceChannel.set_permissions(
            member.guild.default_role, connect=False  # , view_channel=True
        )

        await VoiceChannel.set_permissions(
            member, manage_channels=True, connect=True, speak=True, view_channel=True
        )

        if xe.open is not None:
            openx = xe.open
        else:
            openx = True

        if xe.visible is not None:
            visiblex = xe.visible
        else:
            visiblex = True

        TextChannel = await category.create_text_channel(name=name)

        emb = nextcord.Embed(
            description=f"Если бот не реагирует на нажатие кнопок, запустите команду {self.bot.command_prefix(None, member.guild.id)}войс_сообщение"
        )
        emb.color = nextcord.Colour.random()

        fields = [
            ["✏", "**Изменить название канала**"],
            ["🔒", "**Закрыть канал**"],
            ["👥", "**Ограничить количество пользователей**"],
            ["🎙️", "**За/размутить пользователя**"],
            ["🚪", "**Кикнуть пользователя**"],
            ["⚰️", "**За/разбанить пользователя**"],
            # ["📰", "**Создать/удалить текстовый канал**"],
            ["🔧", "**Установить битрейт канала**"],
            ["🕵️", "**Открыть канал для пользователя**"],
            ["👑", "**Передать права на канал**"],
        ]

        f0 = ""
        for field in fields:
            f0 += f"> {field[0]} - {field[1]}\n"

        emb.add_field(name="Команды", value=f0[:-1], inline=False)

        emb.set_footer(text=f"Спасибо за использование {self.bot.user.name}.")

        emb.add_field(name="Создатель канала", value=member.mention)
        emb.add_field(name="Владелец канала", value=member.mention)
        emb.add_field(name="Статус канала", value=f'{"Открыт" if openx else "Закрыт"}')

        buttons = ControlButtons(self.bot)
        message = await TextChannel.send(embed=emb, view=buttons)
        await message.pin()

        voicechannels.addInfo(
            self.bot.databaseSession,
            member.guild.id,
            VoiceChannel.id,
            TextChannel.id,
            member.id,
            message.id,
        )

        # reactions = ["✏", "🔒", "👥", "🎙️", "🚪", "⚰️", "🔧", "🕵️", "👑"]
        # for reaction in reactions:
        #     await message.add_reaction(reaction)

        await TextChannel.set_permissions(member.guild.default_role, view_channel=False)

        await TextChannel.set_permissions(
            member,
            view_channel=True,
            manage_channels=True,
            read_messages=True,
            read_message_history=True,
            send_messages=True,
        )

        await member.move_to(VoiceChannel)

        if xe.banned is not None:
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

        if xe.opened is not None:
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

        if xe.muted is not None:
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

        if (not openx or not visiblex) and member.guild.id != 876474448126050394:

            if not xe.open:
                await VoiceChannel.set_permissions(
                    member.guild.default_role, connect=False  # , view_channel=True
                )

            if not xe.visible:
                await VoiceChannel.set_permissions(
                    member.guild.default_role, view_channel=False
                )

        await VoiceChannel.set_permissions(
            member.guild.default_role, connect=True  # , view_channel=True
        )

        await buttons.wait()

    async def InPrivate(self, member, after):

        TextChannelUID = voicechannels.getTextChannelByUID(
            self.bot.databaseSession, member.guild.id, after.channel.id
        )
        if TextChannelUID is not None:
            TextChannel = member.guild.get_channel(TextChannelUID)
            if not TextChannel.permissions_for(member).manage_channels:
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

            else:
                try:
                    await TextChannel.set_permissions(
                        member,
                        manage_channel=True,
                        view_channel=True,
                        read_messages=True,
                        read_message_history=True,
                        send_messages=True,
                    )
                except:
                    pass

    async def OutPrivate(self, member, before):

        try:
            await member.edit(mute=False)
            pass
        except:

            if not before.channel.permissions_for(member).speak:
                addVoiceMutes(
                    self.bot.databaseSession,
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
                self.bot.databaseSession, before.channel.guild.id, before.channel.id
            )
            textuid = None
            if xe is not None:
                textuid = xe.txuid
                voicechannels.delChannel(
                    self.bot.databaseSession, before.channel.guild.id, xe
                )
            await before.channel.delete()

            if textuid is not None:
                try:
                    TextChannel = member.guild.get_channel(textuid)
                    await TextChannel.delete()
                except:
                    pass

        else:
            xe = voicechannels.getInfo(
                self.bot.databaseSession, before.channel.guild.id, before.channel.id
            )
            textuid = None
            if xe is not None:
                textuid = xe.txuid

            if textuid is not None:
                TextChannel = member.guild.get_channel(textuid)
                if not TextChannel.permissions_for(member).manage_channels:
                    await TextChannel.set_permissions(member, overwrite=None)
                else:
                    await TextChannel.set_permissions(member, overwrite=None)
                    await TextChannel.set_permissions(member, manage_channel=True)


def setup(bot):
    bot.add_cog(Voice(bot))
