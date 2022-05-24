import asyncio

import nextcord

from checkers import is_stuff
from .ui import ChannelSelector, ChannelModal, ChannelSelectorFromList


def to_binary(a):
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
        self.bot = bot

    @nextcord.ui.button(emoji="✏", style=nextcord.ButtonStyle.secondary)
    async def change_channel_name_button(
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

                binary_name = to_binary(name)

                if not binary_name:
                    name = author.display_name
                    name_for_db = None
                else:
                    name_for_db = name

                try:
                    await author.voice.channel.edit(name=name)
                    self.bot.database.set_voice_channel_name(
                        author.id, channel.guild.id, name_for_db
                    )
                    e = "Успешно изменено!"
                except Exception as el:
                    e = f"При изменении канала произошла ошибка: {el}"

                channel_info = self.bot.database.get_voice_channel(
                    author.voice.channel.id, author.guild.id
                )

                text_channel = author.guild.get_channel(channel_info.text_id)
                await text_channel.edit(name=name)

                await interaction.followup.send(e, ephemeral=True)

    @nextcord.ui.button(emoji="👥", style=nextcord.ButtonStyle.secondary)
    async def limitChannelButton(
        self, button: nextcord.ui.Button, interaction: nextcord.Interaction
    ):
        author = interaction.user

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
                    self.bot.database.set_voice_channel_limit(
                        author.id, author.guild.id, int(slots)
                    )
                except Exception as el:
                    await interaction.followup.send(
                        f"При изменении канала произошла ошибка: {el}", ephemeral=True
                    )

    @nextcord.ui.button(emoji="🔇", style=nextcord.ButtonStyle.secondary)
    async def mute_member_button(
        self, button: nextcord.ui.Button, interaction: nextcord.Interaction
    ):
        author = interaction.user
        channel = await self.bot.fetch_channel(interaction.channel_id)

        if author.voice is not None:

            if author.voice.channel.permissions_for(author).manage_channels:

                selector = ChannelSelector(author, "Пользователь для мута")

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

                if is_stuff(self.bot, author):
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

                            self.bot.database.add_muted(
                                author.id, author.guild.id, member.id
                            )
                        except Exception as el:
                            e = f"При муте произошла ошибка: {el}"
                    else:
                        e = "Пользователь уже в муте!"
                else:
                    e = "Объект не находится в голосовом канале!"

                await interaction.followup.send(e, ephemeral=True)

    @nextcord.ui.button(emoji="🏴", style=nextcord.ButtonStyle.secondary)
    async def ban_member_button(
        self, button: nextcord.ui.Button, interaction: nextcord.Interaction
    ):
        author = interaction.user
        channel = await self.bot.fetch_channel(interaction.channel_id)

        if author.voice is not None:

            if author.voice.channel.permissions_for(author).manage_channels:

                selector = ChannelSelector(author, "Забаневыемый пользователь")

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

                if is_stuff(self.bot, author):
                    return

                if author.voice.channel.permissions_for(member).connect:
                    try:
                        overwrite = nextcord.PermissionOverwrite(connect=False)
                        await member.move_to(None)
                        await author.voice.channel.set_permissions(
                            member, overwrite=overwrite
                        )
                        e = "Успешно забанен!"

                        self.bot.database.add_banned(
                            author.id, author.guild.id, member.id
                        )
                    except Exception as el:
                        e = f"При бане произошла ошибка: {el}"
                else:
                    e = "Пользователь уже находится в бане!"

                await interaction.followup.send(e, ephemeral=True)

    @nextcord.ui.button(emoji="🕵️", style=nextcord.ButtonStyle.secondary)
    async def open_channel_for_button(
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
                            self.bot.database.add_opened(
                                author.id, author.guild.id, member.id
                            )
                            e = f"Успешно раскрыт для {member.name}!"
                        except Exception as el:
                            e = f"При изменении канала произошла ошибка: {el}"
                    else:
                        try:
                            await author.voice.channel.set_permissions(
                                member, overwrite=None
                            )
                            self.bot.database.remove_opened(
                                author.id, author.guild.id, member.id
                            )
                            e = f"Успешно скрыт для {member.name}!"
                        except Exception as el:
                            e = f"При изменении канала произошла ошибка: {el}"

                await interaction.followup.send(e, ephemeral=True)
                # await msg.delete()

    @nextcord.ui.button(emoji="🔒", style=nextcord.ButtonStyle.secondary)
    async def lock_channel_button(
        self, button: nextcord.ui.Button, interaction: nextcord.Interaction
    ):
        author = interaction.user

        if author.voice is not None:

            if author.voice.channel.permissions_for(author).manage_channels:

                await interaction.send(
                    "Подождите, операция выполняется", ephemeral=True
                )

                #

                if author.voice.channel.overwrites_for(
                    author.guild.default_role
                ).connect:
                    try:
                        await author.voice.channel.set_permissions(
                            author.guild.default_role, connect=False
                        )
                        channel_settings = self.bot.database.get_voice_channel_settings(
                            author.id, author.guild.id
                        )
                        channel_settings.open = False
                        self.bot.database.session.commit()
                        e = "Успешно закрыт!"
                    except Exception as el:
                        e = f"При изменении канала произошла ошибка: {el}"

                    channel_info = self.bot.database.get_voice_channel(
                        author.voice.channel.id, author.guild.id
                    )

                    if channel_info.text_id is not None:
                        text_channel = author.guild.get_channel(channel_info.text_id)

                        try:
                            message = await text_channel.fetch_message(
                                channel_info.message_id
                            )
                            emb = message.embeds[0]
                            for field in range(len(emb.fields)):
                                if emb.fields[field].name == "Статус канала":
                                    emb.remove_field(field)
                                    emb.insert_field_at(
                                        index=field,
                                        name="Статус канала",
                                        value="Закрыт",
                                        inline=True,
                                    )

                            await message.edit(embed=emb)
                        except:
                            pass

                else:
                    try:
                        await author.voice.channel.set_permissions(
                            author.guild.default_role, connect=True
                        )
                        channel_settings = self.bot.database.get_voice_channel_settings(
                            author.id, author.guild.id
                        )
                        channel_settings.open = True
                        self.bot.database.session.commit()
                        e = "Успешно открыт!"
                    except Exception as el:
                        e = f"При изменении канала произошла ошибка: {el}"

                    channel_info = self.bot.database.get_voice_channel(
                        author.voice.channel.id, author.guild.id
                    )

                    if channel_info.text_id is not None:
                        text_channel = author.guild.get_channel(channel_info.text_id)

                        try:
                            message = await text_channel.fetch_message(
                                channel_info.message_id
                            )
                            emb = message.embeds[0]
                            for field in range(len(emb.fields)):
                                if emb.fields[field].name == "Статус канала":
                                    emb.remove_field(field)
                                    emb.insert_field_at(
                                        index=field,
                                        name="Статус канала",
                                        value="Открыт",
                                        inline=True,
                                    )

                            await message.edit(embed=emb)
                        except:
                            pass

                await interaction.followup.send(e, ephemeral=True)

    # @nextcord.ui.button(emoji="🔧", style=nextcord.ButtonStyle.secondary)
    async def change_bitrate_button(
        self, button: nextcord.ui.Button, interaction: nextcord.Interaction
    ):
        author = interaction.user

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
                    self.bot.database.set_voice_channel_limit(
                        author.id, author.guild.id, int(bitrate) * 1000
                    )
                    e = "Успешно изменено!"
                except Exception as el:
                    await interaction.followup.send(
                        f"При изменении канала произошла ошибка: {el}", ephemeral=True
                    )

    @nextcord.ui.button(emoji="🚪", style=nextcord.ButtonStyle.secondary)
    async def kick_member_button(
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

                if is_stuff(self.bot, author):
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

    @nextcord.ui.button(emoji="🔊", style=nextcord.ButtonStyle.secondary)
    async def unmute_member_button(
        self, button: nextcord.ui.Button, interaction: nextcord.Interaction
    ):
        author = interaction.user
        channel = await self.bot.fetch_channel(interaction.channel_id)

        if author.voice is not None:

            if author.voice.channel.permissions_for(author).manage_channels:

                await interaction.send(
                    "Подождите, операция выполняется.", ephemeral=True
                )

                members = []

                muted_list = self.bot.database.get_voice_channel_settings(
                    author.id, author.guild.id
                ).muted

                for muted in muted_list:
                    member = author.guild.get_member(muted)
                    if member is not None:
                        members.append(member)

                selector = ChannelSelectorFromList(
                    author, "Пользователь для размута", members
                )

                try:
                    await interaction.followup.send(view=selector, ephemeral=True)
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

                if is_stuff(self.bot, author):
                    return

                if member.voice is not None:

                    if not author.voice.channel.permissions_for(member).speak:
                        try:
                            await member.edit(mute=False)
                            await author.voice.channel.set_permissions(
                                member, overwrite=None
                            )
                            e = "Успешно размучен!"

                            self.bot.database.remove_muted(
                                author.id, author.guild.id, member.id
                            )
                        except Exception as el:
                            e = f"При размуте произошла ошибка: {el}"
                    else:
                        e = "Пользователь не в муте!"

                else:
                    e = "Объект не находится в голосовом канале!"

                await interaction.followup.send(e, ephemeral=True)

    @nextcord.ui.button(emoji="🏳️", style=nextcord.ButtonStyle.secondary)
    async def unban_member_button(
        self, button: nextcord.ui.Button, interaction: nextcord.Interaction
    ):
        author = interaction.user
        channel = await self.bot.fetch_channel(interaction.channel_id)

        if author.voice is not None:

            if author.voice.channel.permissions_for(author).manage_channels:

                await interaction.send(
                    "Подождите, операция выполняется.", ephemeral=True
                )

                members = []

                banned_list = self.bot.database.get_voice_channel_settings(
                    author.id, author.guild.id
                ).banned

                for banned in banned_list:
                    member = author.guild.get_member(banned)
                    if member is not None:
                        members.append(member)

                selector = ChannelSelectorFromList(
                    author, "Разбаневыемый пользователь", members
                )

                try:
                    await interaction.followup.send(view=selector, ephemeral=True)
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

                if is_stuff(self.bot, author):
                    return

                if not author.voice.channel.permissions_for(member).connect:
                    try:
                        await author.voice.channel.set_permissions(
                            member, overwrite=None
                        )
                        e = "Успешно разбанен!"

                        self.bot.database.remove_banned(
                            author.id, author.guild.id, member.id
                        )
                    except Exception as el:
                        e = f"При бане произошла ошибка: {el}"
                else:
                    e = "Пользователь не в бане!"

                await interaction.followup.send(e, ephemeral=True)

    @nextcord.ui.button(emoji="👑", style=nextcord.ButtonStyle.secondary)
    async def change_channel_owner_button(
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

                channel_info = self.bot.database.get_voice_channel(
                    author.voice.channel.id, author.guild.id
                )

                if channel_info.text_id is not None:
                    text_channel = author.guild.get_channel(channel_info.text_id)
                    await text_channel.set_permissions(
                        member,
                        view_channel=True,
                        manage_channels=True,
                        read_messages=True,
                        read_message_history=True,
                        send_messages=True,
                    )
                    await text_channel.set_permissions(author, overwrite=None)

                    try:
                        message = await text_channel.fetch_message(
                            channel_info.message_id
                        )
                        emb = message.embeds[0]
                        for field in range(len(emb.fields)):
                            if emb.fields[field].name == "Владелец канала":
                                emb.remove_field(field)
                                emb.insert_field_at(
                                    index=field,
                                    name="Владелец канала",
                                    value=member.mention,
                                    inline=True,
                                )

                        await message.edit(embed=emb)
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
