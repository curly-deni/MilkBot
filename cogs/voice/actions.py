import nextcord
from additional.check_permission import isAdmin

# database
import database.voicechannels as voicechannels
import database.voicesettings as voicesettings
import database.serversettings as serversettings

# for log
import asyncio

from .ui import ChannelSelector, ChannelModal


def toBinary(a):
    l, m = [], []
    for i in a:
        l.append(ord(i))
    for i in l:
        m.append(int(bin(i)[2:]))
    return m


class ControlButtons(nextcord.ui.View):
    """Channel Control Buttons"""

    def __init__(self, bot):
        super().__init__(timeout=0.0)
        self.value = None
        self.bot = bot

    @nextcord.ui.button(emoji="✏", style=nextcord.ButtonStyle.secondary)
    async def changeChannelNameButton(
        self, button: nextcord.ui.Button, interaction: nextcord.Interaction
    ):
        author = interaction.user
        channel = await self.bot.fetch_channel(interaction.channel_id)

        if author.voice is not None:

            if author.voice.channel.permissions_for(author).manage_channels:

                modal = ChannelModal(
                    "Настройка приватного канала",
                    "Имя канала",
                    "Введите имя канала",
                    min_length=0,
                    required=False,
                )

                try:
                    await interaction.response.send_modal(modal)
                except:
                    return

                await modal.wait()
                name = modal.value()

                binaryName = toBinary(name)

                if binaryName == []:
                    name = author.display_name

                name_for_db = name

                try:
                    await author.voice.channel.edit(name=name)
                    voicesettings.setName(
                        self.bot.databaseSession,
                        channel.guild.id,
                        author.id,
                        name_for_db,
                    )
                    e = "Успешно изменено!"
                except Exception as el:
                    e = f"При изменении канала произошла ошибка: {el}"

                xa = voicechannels.getInfo(
                    self.bot.databaseSession, author.guild.id, author.voice.channel.id
                )
                xb = voicesettings.getInfo(
                    self.bot.databaseSession, author.guild.id, author.id
                )
                if not xb.text or xa.txuid is None:
                    pass

                else:
                    textuid = None
                    if xa.txuid is not None and xa.txuid != "":
                        textuid = xa.txuid

                    if textuid is not None:
                        TextChannel = author.guild.get_channel(textuid)
                        await TextChannel.edit(name=name)

                await interaction.followup.send(e, ephemeral=True)

                # await msg.delete()

    @nextcord.ui.button(emoji="🔒", style=nextcord.ButtonStyle.secondary)
    async def lockChannelButton(
        self, button: nextcord.ui.Button, interaction: nextcord.Interaction
    ):
        author = interaction.user

        if author.voice is not None:

            if author.voice.channel.permissions_for(author).manage_channels:

                await interaction.send(
                    "Подождите, операция выполняется", ephemeral=True
                )

                #

                ss = serversettings.getInfo(self.bot.databaseSession, author.guild.id)
                if ss == "not setup":
                    return

                if author.voice.channel.overwrites_for(
                    author.guild.default_role
                ).connect:
                    try:
                        await author.voice.channel.set_permissions(
                            author.guild.default_role, connect=False
                        )
                        voicesettings.setOpen(
                            self.bot.databaseSession, author.guild.id, author.id, False
                        )
                        e = "Успешно закрыт!"
                    except Exception as el:
                        e = f"При изменении канала произошла ошибка: {el}"

                    xa = voicechannels.getInfo(
                        self.bot.databaseSession,
                        author.guild.id,
                        author.voice.channel.id,
                    )
                    xb = voicesettings.getInfo(
                        self.bot.databaseSession, author.guild.id, author.id
                    )
                    if not xb.text or xa.txuid is None:
                        pass

                    else:
                        textuid = None
                        if xa.txuid is not None and xa.txuid != "":
                            textuid = xa.txuid

                        if textuid is not None:
                            TextChannel = author.guild.get_channel(textuid)
                            msuid = voicechannels.getSettingsMessageUID(
                                self.bot.databaseSession,
                                author.guild.id,
                                author.voice.channel.id,
                            )

                            try:
                                messagex = await TextChannel.fetch_message(msuid)
                                emb = messagex.embeds[0]
                                for field in range(len(emb.fields)):
                                    if emb.fields[field].name == "Статус канала":
                                        emb.remove_field(field)
                                        emb.insert_field_at(
                                            index=field,
                                            name="Статус канала",
                                            value="Закрыт",
                                            inline=True,
                                        )

                                await messagex.edit(embed=emb)
                            except:
                                pass

                else:
                    try:
                        await author.voice.channel.set_permissions(
                            author.guild.default_role, connect=True
                        )
                        voicesettings.setOpen(
                            self.bot.databaseSession, author.guild.id, author.id, True
                        )
                        e = "Успешно открыт!"
                    except Exception as el:
                        e = f"При изменении канала произошла ошибка: {el}"

                    xa = voicechannels.getInfo(
                        self.bot.databaseSession,
                        author.guild.id,
                        author.voice.channel.id,
                    )
                    xb = voicesettings.getInfo(
                        self.bot.databaseSession, author.guild.id, author.id
                    )
                    if not xb.text or xa.txuid is None:
                        pass

                    else:
                        textuid = None
                        if xa.txuid is not None and xa.txuid != "":
                            textuid = xa.txuid

                        if textuid is not None:
                            TextChannel = author.guild.get_channel(textuid)
                            async for message in TextChannel.history(
                                oldest_first=True, limit=None
                            ):
                                messagex = message
                                try:
                                    emb = messagex.embeds[0]
                                    for field in range(len(emb.fields)):
                                        if emb.fields[field].name == "Статус канала":
                                            emb.remove_field(field)
                                            emb.insert_field_at(
                                                index=field,
                                                name="Статус канала",
                                                value="Открыт",
                                                inline=True,
                                            )

                                    await messagex.edit(embed=emb)
                                except:
                                    pass

                await interaction.followup.send(e, ephemeral=True)

    @nextcord.ui.button(emoji="👥", style=nextcord.ButtonStyle.secondary)
    async def limitChannelButton(
        self, button: nextcord.ui.Button, interaction: nextcord.Interaction
    ):
        author = interaction.user
        # channel = await self.bot.fetch_channel(interaction.channel_id)

        if author.voice is not None:

            if author.voice.channel.permissions_for(author).manage_channels:

                modal = ChannelModal(
                    "Настройка приватного канала",
                    "Количество слотов",
                    "Введите количество слотов. 0-максимум",
                )

                try:
                    await interaction.response.send_modal(modal)
                except:
                    return

                await modal.wait()
                slots = modal.value()

                try:
                    await author.voice.channel.edit(user_limit=int(slots))
                    voicesettings.setMaxUser(
                        self.bot.databaseSession,
                        author.guild.id,
                        author.id,
                        int(slots),
                    )
                except Exception as el:
                    await interaction.followup.send(
                        f"При изменении канала произошла ошибка: {el}", ephemeral=True
                    )

                # await msg.delete()

    @nextcord.ui.button(emoji="🚪", style=nextcord.ButtonStyle.secondary)
    async def kickMemberButton(
        self, button: nextcord.ui.Button, interaction: nextcord.Interaction
    ):
        author = interaction.user
        channel = await self.bot.fetch_channel(interaction.channel_id)

        if author.voice is not None:

            if author.voice.channel.permissions_for(author).manage_channels:

                selector = ChannelSelector(author, "Выгоняемый пользователь")

                try:
                    await interaction.send(view=selector, ephemeral=True)
                except:
                    return

                await selector.wait()

                if selector.value != 0:
                    member = author.guild.get_member(selector.value)
                else:
                    await interaction.followup.send(
                        f"{author.mention}, укажите пользователя!", ephemeral=True
                    )

                    try:
                        msg = await self.bot.wait_for(
                            "message",
                            timeout=60.0,
                            check=lambda m: m.channel == channel
                            and m.author.id == author.id,
                        )
                    except asyncio.TimeoutError:
                        return

                    if msg.content.startswith("<"):
                        if msg.content.startswith("<@!"):
                            mid = int(msg.content[3:-1])
                        else:
                            mid = int(msg.content[2:-1])
                    else:
                        mid = int(msg.content)

                    member = author.guild.get_member(mid)
                    await msg.delete()

                ss = serversettings.getInfo(self.bot.databaseSession, author.guild.id)

                if isAdmin(member.roles, ss.adminroles):

                    return

                if member.voice is not None:
                    try:
                        await member.move_to(None)
                        e = "Успешно выгнан!"
                        pass
                    except Exception as el:
                        e = f"При изгнании произошла ошибка: {el}"
                        pass

                else:
                    e = "Объект не находится в голосовом канале!"

                await interaction.followup.send(e, ephemeral=True)

                # await msg.delete()

    @nextcord.ui.button(emoji="🎙️", style=nextcord.ButtonStyle.secondary)
    async def muteMemberButton(
        self, button: nextcord.ui.Button, interaction: nextcord.Interaction
    ):
        author = interaction.user
        channel = await self.bot.fetch_channel(interaction.channel_id)

        if author.voice is not None:

            if author.voice.channel.permissions_for(author).manage_channels:

                selector = ChannelSelector(author, "Пользователь для мута/размута")

                try:
                    await interaction.send(view=selector, ephemeral=True)
                except:
                    return

                await selector.wait()

                if selector.value != 0:
                    member = author.guild.get_member(selector.value)
                else:
                    await interaction.followup.send(
                        f"{author.mention}, укажите пользователя!", ephemeral=True
                    )

                    try:
                        msg = await self.bot.wait_for(
                            "message",
                            timeout=60.0,
                            check=lambda m: m.channel == channel
                            and m.author.id == author.id,
                        )
                    except asyncio.TimeoutError:
                        return

                    if msg.content.startswith("<"):
                        if msg.content.startswith("<@!"):
                            mid = int(msg.content[3:-1])
                        else:
                            mid = int(msg.content[2:-1])
                    else:
                        mid = int(msg.content)

                    member = author.guild.get_member(mid)
                    await msg.delete()

                ss = serversettings.getInfo(self.bot.databaseSession, author.guild.id)

                if isAdmin(member.roles, ss.adminroles):

                    return

                if member.voice is not None:

                    if author.voice.channel.permissions_for(member).speak:
                        try:
                            overwrite = nextcord.PermissionOverwrite(speak=False)
                            await member.edit(mute=True)
                            await author.voice.channel.set_permissions(
                                member, overwrite=overwrite
                            )
                            e = "Успешно замучен!"

                            voicesettings.addMuted(
                                self.bot.databaseSession,
                                author.guild.id,
                                author.id,
                                member.id,
                            )
                            pass
                        except Exception as el:
                            e = f"При муте произошла ошибка: {el}"
                            pass
                    else:
                        try:
                            await member.edit(mute=False)
                            await author.voice.channel.set_permissions(
                                member, overwrite=None
                            )
                            e = "Успешно размучен!"

                            voicesettings.delMuted(
                                self.bot.databaseSession,
                                author.guild.id,
                                author.id,
                                member.id,
                            )
                            pass
                        except Exception as el:
                            e = f"При размуте произошла ошибка: {el}"
                            pass

                else:
                    e = "Объект не находится в голосовом канале!"

                # await channel.send(e)

                # await msg.delete()

    @nextcord.ui.button(emoji="⚰️", style=nextcord.ButtonStyle.secondary)
    async def banMemberButton(
        self, button: nextcord.ui.Button, interaction: nextcord.Interaction
    ):
        author = interaction.user
        channel = await self.bot.fetch_channel(interaction.channel_id)

        if author.voice is not None:

            if author.voice.channel.permissions_for(author).manage_channels:

                selector = ChannelSelector(author, "За/разбаневыемый пользователь")

                try:
                    await interaction.send(view=selector, ephemeral=True)
                except:
                    return

                await selector.wait()

                if selector.value != 0:
                    member = author.guild.get_member(selector.value)
                else:
                    await interaction.followup.send(
                        f"{author.mention}, укажите пользователя!", ephemeral=True
                    )

                    try:
                        msg = await self.bot.wait_for(
                            "message",
                            timeout=60.0,
                            check=lambda m: m.channel == channel
                            and m.author.id == author.id,
                        )
                    except asyncio.TimeoutError:
                        return

                    if msg.content.startswith("<"):
                        if msg.content.startswith("<@!"):
                            mid = int(msg.content[3:-1])
                        else:
                            mid = int(msg.content[2:-1])
                    else:
                        mid = int(msg.content)

                    member = author.guild.get_member(mid)
                    await msg.delete()

                ss = serversettings.getInfo(self.bot.databaseSession, author.guild.id)

                if isAdmin(member.roles, ss.adminroles):

                    return

                if author.voice.channel.permissions_for(member).connect:
                    try:
                        overwrite = nextcord.PermissionOverwrite(connect=False)
                        await member.move_to(None)
                        await author.voice.channel.set_permissions(
                            member, overwrite=overwrite
                        )
                        e = "Успешно забанен!"

                        voicesettings.addBanned(
                            self.bot.databaseSession,
                            author.guild.id,
                            author.id,
                            member.id,
                        )
                        pass
                    except Exception as el:
                        e = f"При бане произошла ошибка: {el}"
                        pass
                else:
                    try:
                        await author.voice.channel.set_permissions(
                            member, overwrite=None
                        )
                        e = "Успешно разбанен!"

                        voicesettings.delBanned(
                            self.bot.databaseSession,
                            author.guild.id,
                            author.id,
                            member.id,
                        )
                        pass
                    except Exception as el:
                        e = f"При разбане произошла ошибка: {el}"
                        pass

                await interaction.followup.send(e, ephemeral=True)
                # await msg.delete()

    @nextcord.ui.button(emoji="🔧", style=nextcord.ButtonStyle.secondary)
    async def changeBitrateButton(
        self, button: nextcord.ui.Button, interaction: nextcord.Interaction
    ):
        author = interaction.user
        channel = await self.bot.fetch_channel(interaction.channel_id)

        if author.voice is not None:

            if author.voice.channel.permissions_for(author).manage_channels:

                modal = ChannelModal(
                    "Настройка приватного канала",
                    "Битрейт",
                    "Введите битрейт канала в Килобайтах",
                )

                try:
                    await interaction.response.send_modal(modal)
                except:
                    return

                await modal.wait()
                bitrate = modal.value()

                try:
                    await author.voice.channel.edit(bitrate=int(bitrate) * 1000)
                    voicesettings.setBitrate(
                        self.bot.databaseSession,
                        author.guild.id,
                        author.id,
                        int(bitrate) * 1000,
                    )
                    e = "Успешно изменено!"
                except Exception as el:
                    await interaction.followup.send(
                        f"При изменении канала произошла ошибка: {el}", ephemeral=True
                    )

    @nextcord.ui.button(emoji="👑", style=nextcord.ButtonStyle.secondary)
    async def changeChannelOwnerButton(
        self, button: nextcord.ui.Button, interaction: nextcord.Interaction
    ):
        author = interaction.user
        channel = await self.bot.fetch_channel(interaction.channel_id)

        if author.voice is not None:

            if author.voice.channel.permissions_for(author).manage_channels:

                selector = ChannelSelector(author, "Новый владелец канала")

                try:
                    await interaction.send(view=selector, ephemeral=True)
                except:
                    return

                await selector.wait()

                if selector.value != 0:
                    member = author.guild.get_member(selector.value)
                else:
                    await interaction.followup.send(
                        f"{author.mention}, укажите пользователя!", ephemeral=True
                    )

                    try:
                        msg = await self.bot.wait_for(
                            "message",
                            timeout=60.0,
                            check=lambda m: m.channel == channel
                            and m.author.id == author.id,
                        )
                    except asyncio.TimeoutError:
                        return

                    if msg.content.startswith("<"):
                        if msg.content.startswith("<@!"):
                            mid = int(msg.content[3:-1])
                        else:
                            mid = int(msg.content[2:-1])
                    else:
                        mid = int(msg.content)

                    member = author.guild.get_member(mid)
                    await msg.delete()

                await author.voice.channel.set_permissions(
                    member,
                    manage_channels=True,
                    connect=True,
                    speak=True,
                    view_channel=True,
                )

                xa = voicechannels.getInfo(
                    self.bot.databaseSession, author.guild.id, author.voice.channel.id
                )
                xb = voicesettings.getInfo(
                    self.bot.databaseSession, author.guild.id, author.id
                )
                if not xb.text or xa.txuid is None:
                    pass

                else:
                    textuid = None
                    if xa.txuid is not None and xa.txuid != "":
                        textuid = xa.txuid

                    if textuid is not None:
                        TextChannel = author.guild.get_channel(textuid)
                        await TextChannel.set_permissions(
                            member,
                            view_channel=True,
                            manage_channels=True,
                            read_messages=True,
                            read_message_history=True,
                            send_messages=True,
                        )
                        await TextChannel.set_permissions(author, overwrite=None)
                        msuid = voicechannels.getSettingsMessageUID(
                            self.bot.databaseSession,
                            author.guild.id,
                            author.voice.channel.id,
                        )

                        try:
                            messagex = await TextChannel.fetch_message(msuid)
                            emb = messagex.embeds[0]
                            for field in range(len(emb.fields)):
                                if emb.fields[field].name == "Владелец канала":
                                    emb.remove_field(field)
                                    emb.insert_field_at(
                                        index=field,
                                        name="Владелец канала",
                                        value=member.mention,
                                        inline=True,
                                    )

                            await messagex.edit(embed=emb)
                        except:
                            pass

                await interaction.send("Владелец успешно изменён!", ephemeral=True)

                await author.voice.channel.set_permissions(author, overwrite=None)

                await author.voice.channel.set_permissions(
                    author,
                    view_channel=True,
                    read_messages=True,
                    read_message_history=True,
                    send_messages=True,
                )

                # await msg.delete()

    @nextcord.ui.button(emoji="🕵️", style=nextcord.ButtonStyle.secondary)
    async def openChannelForButton(
        self, button: nextcord.ui.Button, interaction: nextcord.Interaction
    ):
        author = interaction.user
        channel = await self.bot.fetch_channel(interaction.channel_id)

        if author.voice is not None:

            if author.voice.channel.permissions_for(author).manage_channels:

                selector = ChannelSelector(author, "Пользователь")

                try:
                    await interaction.send(view=selector, ephemeral=True)
                except:
                    return

                await selector.wait()

                if selector.value != 0:
                    member = author.guild.get_member(selector.value)
                else:
                    await interaction.followup.send(
                        f"{author.mention}, укажите пользователя!", ephemeral=True
                    )

                    try:
                        msg = await self.bot.wait_for(
                            "message",
                            timeout=60.0,
                            check=lambda m: m.channel == channel
                            and m.author.id == author.id,
                        )
                    except asyncio.TimeoutError:
                        return

                    if msg.content.startswith("<"):
                        if msg.content.startswith("<@!"):
                            mid = int(msg.content[3:-1])
                        else:
                            mid = int(msg.content[2:-1])
                    else:
                        mid = int(msg.content)

                    member = author.guild.get_member(mid)
                    await msg.delete()

                if author.voice.channel.permissions_for(
                    member.guild.default_role
                ).connect:
                    e = "Канал не скрыт!"
                    pass

                else:
                    if not author.voice.channel.permissions_for(member).connect:
                        try:
                            await author.voice.channel.set_permissions(
                                member, view_channel=True, connect=True
                            )
                            voicesettings.addOpened(
                                self.bot.databaseSession,
                                author.guild.id,
                                author.id,
                                member.id,
                            )
                            e = f"Успешно раскрыт для {member.name}!"
                        except Exception as el:
                            e = f"При изменении канала произошла ошибка: {el}"
                    else:
                        try:
                            await author.voice.channel.set_permissions(
                                member, overwrite=None
                            )
                            voicesettings.delOpened(
                                self.bot.databaseSession,
                                author.guild.id,
                                author.id,
                                member.id,
                            )
                            e = f"Успешно скрыт для {member.name}!"
                        except Exception as el:
                            e = f"При изменении канала произошла ошибка: {el}"

                await interaction.followup.send(e, ephemeral=True)
                # await msg.delete()
