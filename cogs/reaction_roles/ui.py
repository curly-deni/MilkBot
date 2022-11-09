import nextcord
from typing import Optional


class NewReactionRolesSetup(nextcord.ui.View):
    def __init__(self, author: nextcord.Member, bot):
        super().__init__(timeout=1200.0)
        self.bot = bot
        self.author: nextcord.Member = author
        self.control_message: Optional[nextcord.Message] = None
        self.preview_message: Optional[nextcord.Message] = None
        self.original_channel: Optional[nextcord.TextChannel] = None

        self.embed = nextcord.Embed(title="Эмодзи и закрепленные роли")

        self.add_button = nextcord.ui.Button(label="Добавить")
        self.add_item(self.add_button)

        self.batch_button = nextcord.ui.Button(label="Добавить несколько")
        self.add_item(self.batch_button)

        self.delete_button = nextcord.ui.Button(label="Удалить")
        self.add_item(self.delete_button)

        self.unique_selector = nextcord.ui.Select(
            placeholder="Только одна выбранная роль",
            options=[
                nextcord.SelectOption(label="Да", value="1"),
                nextcord.SelectOption(label="Нет", value="0"),
            ],
        )
        self.unique_set = False
        self.add_item(self.unique_selector)

        self.single_use_selector = nextcord.ui.Select(
            placeholder="Однократное использование",
            options=[
                nextcord.SelectOption(label="Да", value="1"),
                nextcord.SelectOption(label="Нет", value="0"),
            ],
        )
        self.single_use_set = False
        self.add_item(self.single_use_selector)

        self.send_button: nextcord.ui.Button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.green, label="Сохранить", disabled=True
        )
        self.add_item(self.send_button)

        self.cancel_button: nextcord.ui.Button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.red, label="Отмена"
        )
        self.add_item(self.cancel_button)

        self.reaction_and_roles = {}
        self.unique = False
        self.single_use = False

    async def interaction_check(self, interaction: nextcord.Interaction):
        if self.author == interaction.user:
            match interaction.data["custom_id"]:
                case self.add_button.custom_id:
                    request_emoji_message = await interaction.send("Укажите эмозди")
                    try:
                        emoji_message: nextcord.Message = await self.bot.wait_for(
                            "message",
                            check=lambda msg: msg.author == self.author
                            and msg.channel == self.original_channel,
                            timeout=60.0,
                        )
                    except TimeoutError:
                        await request_emoji_message.delete()
                        return
                    try:
                        await self.preview_message.add_reaction(emoji_message.content)
                    except:
                        fail_message = await self.original_channel.send(
                            "Некорректное эмодзи"
                        )
                        await request_emoji_message.delete()
                        await emoji_message.delete()
                        await fail_message.delete()
                        return

                    request_role_message = await interaction.send(
                        "Укажите ID роли, или упомяните её"
                    )
                    try:
                        role_message: nextcord.Message = await self.bot.wait_for(
                            "message",
                            check=lambda msg: msg.author == self.author
                            and msg.channel == self.original_channel,
                            timeout=60.0,
                        )
                    except TimeoutError:
                        await request_emoji_message.delete()
                        await emoji_message.delete()
                        await request_role_message.delete()
                        return

                    if not role_message.role_mentions:

                        async def uncorrect_role():
                            await self.preview_message.clear_reaction(
                                emoji_message.content
                            )
                            fail_message = await self.original_channel.send(
                                "Некорректная роль"
                            )
                            await request_emoji_message.delete()
                            await emoji_message.delete()
                            await request_role_message.delete()
                            await role_message.delete()
                            await fail_message.delete()
                            return

                        role_id = (
                            role_message.content.replace("<", "")
                            .replace(">", "")
                            .replace("@", "")
                            .replace("&", "")
                        )
                        if not role_id.isdigit():
                            await uncorrect_role()
                            return

                        role = self.original_channel.guild.get_role(int(role_id))
                        if role is None:
                            await uncorrect_role()
                            return
                    else:
                        role = role_message.role_mentions[0]

                    self.reaction_and_roles[emoji_message.content] = role.id
                    self.embed.description = ""
                    for emoji_id, role_id in self.reaction_and_roles.items():
                        self.embed.description += f"{emoji_id} - <@&{role_id}>\n"

                    if self.preview_message is not None:
                        await self.preview_message.edit(embed=self.embed)
                    await request_emoji_message.delete()
                    await emoji_message.delete()
                    await request_role_message.delete()
                    await role_message.delete()

                case self.delete_button.custom_id:
                    request_emoji_message = await interaction.send("Укажите эмозди")
                    try:
                        emoji_message: nextcord.Message = await self.bot.wait_for(
                            "message",
                            check=lambda msg: msg.author == self.author
                            and msg.channel == self.original_channel,
                            timeout=60.0,
                        )
                    except TimeoutError:
                        await request_emoji_message.delete()
                        return

                    if emoji_message.content not in self.reaction_and_roles:
                        fail_message = await self.original_channel.send(
                            "Данное эмодзи отсутсвует"
                        )
                        await request_emoji_message.delete()
                        await emoji_message.delete()
                        await fail_message.delete()
                        return

                    await self.preview_message.clear_reaction(emoji_message.content)
                    del self.reaction_and_roles[emoji_message.content]

                    self.embed.description = ""
                    for emoji_id, role_id in self.reaction_and_roles.items():
                        self.embed.description += f"{emoji_id} - <@&{role_id}>\n"

                    if self.preview_message is not None:
                        await self.preview_message.edit(embed=self.embed)
                    await request_emoji_message.delete()
                    await emoji_message.delete()
                case self.send_button.custom_id:
                    status_messages = []

                    async def del_status():
                        for i in status_messages:
                            try:
                                await i.delete()
                            except:
                                continue

                    if self.reaction_and_roles == {}:
                        await interaction.send("Не добавлено **ни одного** эмодзи")

                    status_messages.append(
                        await interaction.send("Введите ID чата, или упомяните его.")
                    )
                    channel_id = await self.bot.wait_for(
                        "message",
                        check=lambda message: message.author == self.author
                        and message.channel == self.original_channel,
                    )
                    channel_id.content = (
                        channel_id.content.replace("#", "")
                        .replace("<", "")
                        .replace(">", "")
                    )
                    if not (channel_id.content).isdigit():
                        await self.original_channel.send("Некорректный ID")
                        await del_status()
                        return
                    channel: Optional[nextcord.TextChannel] = self.bot.get_channel(
                        int(channel_id.content)
                    )
                    if channel is None:
                        await self.original_channel.send(
                            f"Не найден канал с ID {channel_id.content}"
                        )
                        await del_status()
                        return
                    else:
                        status_messages.append(
                            await self.original_channel.send(
                                f"Выбран канал **{channel.name}** ({channel.id})"
                            )
                        )

                    status_messages.append(
                        await self.original_channel.send("Введите ID сообщения")
                    )
                    message_id = await self.bot.wait_for(
                        "message",
                        check=lambda message: message.author == self.author
                        and message.channel == self.original_channel,
                    )
                    if not (message_id.content).isdigit():
                        await self.original_channel.send("Некорректный ID")
                        await del_status()
                        return
                    message = await channel.fetch_message(int(message_id.content))
                    if message is None:
                        await self.original_channel.send(
                            f"Не найдено сообщение с ID {message_id.content }"
                        )
                        await del_status()
                        return
                    else:
                        status_messages.append(
                            await self.original_channel.send("Сообщение выбрано")
                        )

                    for emoji_id in self.reaction_and_roles:
                        try:
                            await message.add_reaction(emoji_id)
                        except:
                            continue

                    await self.control_message.delete()
                    await self.preview_message.delete()
                    await channel_id.delete()
                    await message_id.delete()
                    await del_status()

                    self.bot.database.add_reaction_roles_info(
                        message.id,
                        channel.id,
                        self.author.id,
                        self.reaction_and_roles,
                        self.unique,
                        self.single_use,
                    )

                    await self.original_channel.send("Сообщение успешно отправлено!")
                    self.stop()
                case self.cancel_button.custom_id:
                    await self.on_timeout()
                    self.stop()
                case self.unique_selector.custom_id:
                    self.unique = bool(int(self.unique_selector.values[0]))
                    self.unique_set = True
                    content_message = (
                        f"**Только одна выбранная роль:** {'Да' if self.unique else 'Нет'}\n"
                        + f"**Однократное использование:** {'Да' if self.single_use else 'Нет'}\n"
                    )
                    if (
                        self.unique_set
                        and self.single_use_set
                        and self.send_button.disabled
                    ):
                        self.send_button.disabled = False
                        if self.control_message is not None:
                            await self.control_message.edit(view=self)
                    if self.preview_message is not None:
                        await self.preview_message.edit(content=content_message)
                    return True
                case self.batch_button.custom_id:
                    request_emoji_message = await interaction.send(
                        "Укажите эмозди (в формате 'эмодзи - роль')"
                    )
                    try:
                        emoji_message: nextcord.Message = await self.bot.wait_for(
                            "message",
                            check=lambda msg: msg.author == self.author
                            and msg.channel == self.original_channel,
                            timeout=60.0,
                        )
                    except TimeoutError:
                        await request_emoji_message.delete()
                        return

                    batch = emoji_message.content.split("\n")
                    for i in batch:
                        pr = (
                            i.replace(" ", "")
                            .replace("<", "")
                            .replace(">", "")
                            .replace("@", "")
                            .replace("&", "")
                        )
                        emoji = pr.split("-")[0]
                        id = pr.split("-")[1]
                        if not id.isdigit():
                            continue
                        try:
                            await self.preview_message.add_reaction(emoji)
                        except:
                            continue

                        role = self.original_channel.guild.get_role(int(id))
                        if role is None:
                            await self.preview_message.clear_reaction(emoji)
                            continue

                        self.reaction_and_roles[emoji] = role.id
                    self.embed.description = ""
                    for emoji_id, role_id in self.reaction_and_roles.items():
                        self.embed.description += f"{emoji_id} - <@&{role_id}>\n"

                    if self.preview_message is not None:
                        await self.preview_message.edit(embed=self.embed)
                    await request_emoji_message.delete()
                    await emoji_message.delete()
                case self.single_use_selector.custom_id:
                    self.single_use = bool(int(self.single_use_selector.values[0]))
                    self.single_use_set = True
                    content_message = (
                        f"**Только одна выбранная роль:** {'Да' if self.unique else 'Нет'}\n"
                        + f"**Однократное использование:** {'Да' if self.single_use else 'Нет'}\n"
                    )
                    if (
                        self.unique_set
                        and self.single_use_set
                        and self.send_button.disabled
                    ):
                        self.send_button.disabled = False
                        if self.control_message is not None:
                            await self.control_message.edit(view=self)
                    if self.preview_message is not None:
                        await self.preview_message.edit(content=content_message)
                    return True
        else:
            await interaction.send("У вас нет прав на это действие!", ephemeral=True)
        return True

    async def on_timeout(self) -> None:
        for child in self.children:
            try:
                child.disabled = True
            except AttributeError:
                continue

        if self.control_message:
            await self.control_message.edit(view=self)


class ExReactionRolesSetup(nextcord.ui.View):
    def __init__(self, author: nextcord.Member, bot, message, db_info):
        super().__init__(timeout=1200.0)
        self.bot = bot
        self.author: nextcord.Member = author
        self.control_message: Optional[nextcord.Message] = None
        self.preview_message: Optional[nextcord.Message] = None
        self.original_channel: Optional[nextcord.TextChannel] = None

        self.embed = nextcord.Embed(title="Эмодзи и закрепленные роли")
        self.message: Optional[nextcord.Message] = message
        self.db_info = db_info

        self.reaction_and_roles = {}
        for roles_info in db_info.roles:
            emoji = roles_info.split("#")[0]
            role = roles_info.split("#")[1]

            self.reaction_and_roles[emoji] = role

        self.embed.description = ""
        for emoji_id, role_id in self.reaction_and_roles.items():
            self.embed.description += f"{emoji_id} - <@&{role_id}>\n"

        self.unique = db_info.unique
        self.single_use = db_info.single_use

        self.add_button = nextcord.ui.Button(label="Добавить")
        self.add_item(self.add_button)

        self.batch_button = nextcord.ui.Button(label="Добавить несколько")
        self.add_item(self.batch_button)

        self.delete_button = nextcord.ui.Button(label="Удалить")
        self.add_item(self.delete_button)

        self.unique_selector = nextcord.ui.Select(
            placeholder="Только одна выбранная роль",
            options=[
                nextcord.SelectOption(label="Да", value="1", default=self.unique),
                nextcord.SelectOption(label="Нет", value="0", default=not self.unique),
            ],
        )
        self.unique_set = True
        self.add_item(self.unique_selector)

        self.single_use_selector = nextcord.ui.Select(
            placeholder="Однократное использование",
            options=[
                nextcord.SelectOption(label="Да", value="1", default=self.single_use),
                nextcord.SelectOption(
                    label="Нет", value="0", default=not self.single_use
                ),
            ],
        )
        self.single_use_set = True
        self.add_item(self.single_use_selector)

        self.send_button: nextcord.ui.Button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.green, label="Сохранить"
        )
        self.add_item(self.send_button)

        self.cancel_button: nextcord.ui.Button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.red, label="Отмена"
        )
        self.add_item(self.cancel_button)

    async def interaction_check(self, interaction: nextcord.Interaction):
        if self.author == interaction.user:
            match interaction.data["custom_id"]:
                case self.add_button.custom_id:
                    request_emoji_message = await interaction.send("Укажите эмозди")
                    try:
                        emoji_message: nextcord.Message = await self.bot.wait_for(
                            "message",
                            check=lambda msg: msg.author == self.author
                            and msg.channel == self.original_channel,
                            timeout=60.0,
                        )
                    except TimeoutError:
                        await request_emoji_message.delete()
                        return
                    try:
                        await self.preview_message.add_reaction(emoji_message.content)
                    except:
                        fail_message = await self.original_channel.send(
                            "Некорректное эмодзи"
                        )
                        await request_emoji_message.delete()
                        await emoji_message.delete()
                        await fail_message.delete()
                        return

                    request_role_message = await interaction.send(
                        "Укажите ID роли, или упомяните её"
                    )
                    try:
                        role_message: nextcord.Message = await self.bot.wait_for(
                            "message",
                            check=lambda msg: msg.author == self.author
                            and msg.channel == self.original_channel,
                            timeout=60.0,
                        )
                    except TimeoutError:
                        await request_emoji_message.delete()
                        await emoji_message.delete()
                        await request_role_message.delete()
                        return

                    if not role_message.role_mentions:

                        async def uncorrect_role():
                            await self.preview_message.clear_reaction(
                                emoji_message.content
                            )
                            fail_message = await self.original_channel.send(
                                "Некорректная роль"
                            )
                            await request_emoji_message.delete()
                            await emoji_message.delete()
                            await request_role_message.delete()
                            await role_message.delete()
                            await fail_message.delete()
                            return

                        role_id = (
                            role_message.content.replace("<", "")
                            .replace(">", "")
                            .replace("@", "")
                            .replace("&", "")
                        )
                        if not role_id.isdigit():
                            await uncorrect_role()
                            return

                        role = self.original_channel.guild.get_role(int(role_id))
                        if role is None:
                            await uncorrect_role()
                            return
                    else:
                        role = role_message.role_mentions[0]

                    self.reaction_and_roles[emoji_message.content] = role.id
                    self.embed.description = ""
                    for emoji_id, role_id in self.reaction_and_roles.items():
                        self.embed.description += f"{emoji_id} - <@&{role_id}>\n"

                    if self.preview_message is not None:
                        await self.preview_message.edit(embed=self.embed)
                    await request_emoji_message.delete()
                    await emoji_message.delete()
                    await request_role_message.delete()
                    await role_message.delete()

                case self.batch_button.custom_id:
                    request_emoji_message = await interaction.send(
                        "Укажите эмозди (в формате 'эмодзи - роль')"
                    )
                    try:
                        emoji_message: nextcord.Message = await self.bot.wait_for(
                            "message",
                            check=lambda msg: msg.author == self.author
                            and msg.channel == self.original_channel,
                            timeout=60.0,
                        )
                    except TimeoutError:
                        await request_emoji_message.delete()
                        return

                    batch = emoji_message.content.split("\n")
                    for i in batch:
                        pr = (
                            i.replace(" ", "")
                            .replace("<", "")
                            .replace(">", "")
                            .replace("@", "")
                            .replace("&", "")
                        )
                        emoji = pr.split("-")[0]
                        id = pr.split("-")[1]
                        if not id.isdigit():
                            continue
                        try:
                            await self.preview_message.add_reaction(emoji)
                        except:
                            continue

                        role = self.original_channel.guild.get_role(int(id))
                        if role is None:
                            await self.preview_message.clear_reaction(emoji)
                            continue

                        self.reaction_and_roles[emoji] = role.id
                    self.embed.description = ""
                    for emoji_id, role_id in self.reaction_and_roles.items():
                        self.embed.description += f"{emoji_id} - <@&{role_id}>\n"

                    if self.preview_message is not None:
                        await self.preview_message.edit(embed=self.embed)
                    await request_emoji_message.delete()
                    await emoji_message.delete()

                case self.delete_button.custom_id:
                    request_emoji_message = await interaction.send("Укажите эмозди")
                    try:
                        emoji_message: nextcord.Message = await self.bot.wait_for(
                            "message",
                            check=lambda msg: msg.author == self.author
                            and msg.channel == self.original_channel,
                            timeout=60.0,
                        )
                    except TimeoutError:
                        await request_emoji_message.delete()
                        return

                    if emoji_message.content not in self.reaction_and_roles:
                        fail_message = await self.original_channel.send(
                            "Данное эмодзи отсутсвует"
                        )
                        await request_emoji_message.delete()
                        await emoji_message.delete()
                        await fail_message.delete()
                        return

                    await self.preview_message.clear_reaction(emoji_message.content)
                    del self.reaction_and_roles[emoji_message.content]

                    self.embed.description = ""
                    for emoji_id, role_id in self.reaction_and_roles.items():
                        self.embed.description += f"{emoji_id} - <@&{role_id}>\n"

                    if self.preview_message is not None:
                        await self.preview_message.edit(embed=self.embed)
                    await request_emoji_message.delete()
                    await emoji_message.delete()
                case self.send_button.custom_id:
                    await self.message.clear_reactions()

                    for emoji_id in self.reaction_and_roles:
                        await self.message.add_reaction(emoji_id)

                    await self.control_message.delete()
                    await self.preview_message.delete()

                    self.bot.database.add_reaction_roles_info(
                        self.message.id,
                        self.message.channel.id,
                        self.author.id,
                        self.reaction_and_roles,
                        self.unique,
                        self.single_use,
                    )

                    await self.original_channel.send("Сообщение успешно отправлено!")
                    self.stop()
                case self.cancel_button.custom_id:
                    await self.on_timeout()
                    self.stop()
                case self.unique_selector.custom_id:
                    self.unique = bool(int(self.unique_selector.values[0]))
                    self.unique_set = True
                    content_message = (
                        f"**Только одна выбранная роль:** {'Да' if self.unique else 'Нет'}\n"
                        + f"**Однократное использование:** {'Да' if self.single_use else 'Нет'}\n"
                    )
                    if (
                        self.unique_set
                        and self.single_use_set
                        and self.send_button.disabled
                    ):
                        self.send_button.disabled = False
                        if self.control_message is not None:
                            await self.control_message.edit(view=self)
                    if self.preview_message is not None:
                        await self.preview_message.edit(content=content_message)
                    return True
                case self.single_use_selector.custom_id:
                    self.single_use = bool(int(self.single_use_selector.values[0]))
                    self.single_use_set = True
                    content_message = (
                        f"**Только одна выбранная роль:** {'Да' if self.unique else 'Нет'}\n"
                        + f"**Однократное использование:** {'Да' if self.single_use else 'Нет'}\n"
                    )
                    if (
                        self.unique_set
                        and self.single_use_set
                        and self.send_button.disabled
                    ):
                        self.send_button.disabled = False
                        if self.control_message is not None:
                            await self.control_message.edit(view=self)
                    if self.preview_message is not None:
                        await self.preview_message.edit(content=content_message)
                    return True
        else:
            await interaction.send("У вас нет прав на это действие!", ephemeral=True)
        return True

    async def on_timeout(self) -> None:
        for child in self.children:
            try:
                child.disabled = True
            except AttributeError:
                continue

        if self.control_message:
            await self.control_message.edit(view=self)
