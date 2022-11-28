from typing import Optional

import nextcord
from modules.ui import FieldModal
from validators import url

actions = {
    "hug": "Обьятие",
    "smile": "Улыбка",
    "poke": "Тык",
    "slap": "Пощёчина",
    "bite": "Укус",
    "cry": "Рыдание",
    "blush": "Краснение",
    "kiss": "Поцелуй",
    "lick": "Облизывание",
    "pat": "Поглаживание",
    "feed": "Кормление",
}


class GIFandImageSetuper(nextcord.ui.View):
    def __init__(self, author: nextcord.Member, bot, gif: list, type):
        super().__init__(timeout=800.0)
        self.bot = bot
        self.author: nextcord.Member = author
        self.control_message: Optional[nextcord.Message] = None
        self.preview_message: Optional[nextcord.Message] = None

        self.gif_list = gif
        self.type = type
        self.index = 0

        self.previous_page = nextcord.ui.Button(emoji="⬅️", disabled=True)
        self.add_item(self.previous_page)
        self.next_page = nextcord.ui.Button(emoji="➡️", disabled=True)
        self.add_item(self.next_page)

        self.embed = nextcord.Embed(
            title=actions.get(self.type, "Неизвестное действие")
        )
        if self.gif_list:
            self.embed.set_footer(text=f"Изображение 1 из {len(self.gif_list)}")
            self.next_page.disabled = False
            self.embed.set_image(url=self.gif_list[0])
        else:
            self.embed.set_footer(text=f"Изображение 0 из 0")

        self.add_button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.green, label="Добавить"
        )
        self.add_item(self.add_button)
        self.batch_button = nextcord.ui.Button(label="Добавить несколько")
        # self.add_item(self.batch_button)
        self.delete_button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.red, label="Удалить"
        )
        self.add_item(self.delete_button)
        self.stop_button = nextcord.ui.Button(label="Закончить")
        self.add_item(self.stop_button)

    async def interaction_check(self, interaction: nextcord.Interaction):
        if self.author != interaction.user:
            return await interaction.send(
                "У вас нет прав на это действие!", ephemeral=True
            )

        match interaction.data["custom_id"]:
            case self.stop_button.custom_id:
                await self.on_timeout()
                self.stop()
            case self.add_button.custom_id:
                modal = FieldModal(
                    title=f"GIF для действия", label="URL", placeholder="URL"
                )
                await interaction.response.send_modal(modal)
                await modal.wait()
                value = modal.value()
                try:
                    if not url(value):
                        return await interaction.followup.send("Неверный URL")
                except:
                    return await interaction.followup.send("Неверный URL")
                self.gif_list.append(value)
                self.index = self.gif_list.index(value)
                self.embed.set_footer(
                    text=f"Изображение {self.index + 1} из {len(self.gif_list)}"
                )
                self.embed.set_image(url=self.gif_list[self.index])
                if len(self.gif_list) > 1:
                    self.previous_page.disabled = False
                if self.index + 1 >= len(self.gif_list):
                    self.next_page.disabled = True
                if self.control_message is not None:
                    try:
                        await self.control_message.edit(view=self)
                    except:
                        pass
                if self.preview_message is not None:
                    try:
                        await self.preview_message.edit(embed=self.embed)
                    except:
                        pass
            case self.delete_button.custom_id:
                if not self.gif_list:
                    return await interaction.send("Отстуствтуют сообщения")
                self.gif_list.pop(self.index)
                self.index += -1
                if self.index < 0:
                    self.index = 0
                if self.index - 1 <= 0:
                    self.previous_page.disabled = True
                if len(self.gif_list) <= 1:
                    self.next_page.disabled = True
                if self.gif_list:
                    self.embed.set_footer(
                        text=f"Изображение {self.index + 1} из {len(self.gif_list)}"
                    )
                    self.embed.set_image(url=self.gif_list[self.index])
                else:
                    self.embed.set_footer(text=f"Изображение 0 из 0")
                    self.embed.set_image(url=None)
                if self.control_message is not None:
                    try:
                        await self.control_message.edit(view=self)
                    except:
                        pass
                if self.preview_message is not None:
                    try:
                        await self.preview_message.edit(embed=self.embed)
                    except:
                        pass
            case self.batch_button.custom_id:
                pass
            case self.previous_page.custom_id:
                if self.index < 0:
                    return await interaction.send("Вы достигли конца!")
                self.index += -1
                self.embed.set_footer(
                    text=f"Изображение {self.index + 1} из {len(self.gif_list)}"
                )
                self.embed.set_image(url=self.gif_list[self.index])
                self.next_page.disabled = False
                if self.index - 1 <= 0:
                    self.previous_page.disabled = True
                if self.control_message is not None:
                    try:
                        await self.control_message.edit(view=self)
                    except:
                        pass
                if self.preview_message is not None:
                    try:
                        await self.preview_message.edit(embed=self.embed)
                    except:
                        pass
            case self.next_page.custom_id:
                if self.index > len(self.gif_list):
                    return await interaction.send("Вы достигли конца!")
                self.index += 1
                self.embed.set_footer(
                    text=f"Изображение {self.index + 1} из {len(self.gif_list)}"
                )
                self.embed.set_image(url=self.gif_list[self.index])
                self.previous_page.disabled = False
                if self.index + 1 >= len(self.gif_list):
                    self.next_page.disabled = True
                if self.control_message is not None:
                    try:
                        await self.control_message.edit(view=self)
                    except:
                        pass
                if self.preview_message is not None:
                    try:
                        await self.preview_message.edit(embed=self.embed)
                    except:
                        pass
        return True

    async def on_timeout(self) -> None:
        for child in self.children:
            try:
                child.disabled = True
            except AttributeError:
                continue

        if self.control_message:
            await self.control_message.edit(view=self)


def parse_color(content: str):
    if content.startswith("#"):
        try:
            return int(content[1:], 16)
        except:
            return nextcord.Colour.random()
    else:
        return nextcord.Colour.random()


class ReactionRolesSetup(nextcord.ui.View):
    def __init__(
        self,
        author: nextcord.Member,
        bot,
        channel: nextcord.TextChannel,
        message: Optional[nextcord.Message],
        db_info=None,
        edit_existing=False,
    ):
        super().__init__(timeout=1200.0)
        self.bot = bot
        self.author: nextcord.Member = author
        self.control_message: Optional[nextcord.Message] = None
        self.preview_message: Optional[nextcord.Message] = None
        self.original_channel: Optional[nextcord.TextChannel] = None

        self.channel = channel
        self.message = message

        self.add_button = nextcord.ui.Button(label="Добавить", row=0)
        self.add_item(self.add_button)

        self.batch_button = nextcord.ui.Button(label="Добавить несколько", row=0)
        self.add_item(self.batch_button)

        self.delete_button = nextcord.ui.Button(label="Удалить", row=0)
        self.add_item(self.delete_button)

        self.text = ""
        self.message_text = ""

        self.colour_button = nextcord.ui.Button(label="Цвет", row=1)
        self.title_button = nextcord.ui.Button(label="Заголовок", row=1)
        self.text_button = nextcord.ui.Button(label="Текст", row=1)
        self.icon_button = nextcord.ui.Button(label="Иконка", row=1)
        self.message_button = nextcord.ui.Button(label="Сообщение", row=1)
        if message is not None and not edit_existing:
            self.embed = nextcord.Embed(title="Эмодзи и закрепленные роли")
        else:
            self.embed = nextcord.Embed(title="Предпросмотр")

            self.add_item(self.colour_button)
            self.add_item(self.title_button)
            self.add_item(self.text_button)
            self.add_item(self.icon_button)
            self.add_item(self.message_button)

        self.db_info = db_info
        self.edit_existing = edit_existing
        self.reaction_and_roles = {}
        if db_info is not None:
            self.unique = db_info.unique
            self.single_use = db_info.single_use

            for roles_info in db_info.roles:
                emoji = roles_info.split("#")[0]
                role = roles_info.split("#")[1]

                self.reaction_and_roles[emoji] = role

            self.embed.description = ""
            for emoji_id, role_id in self.reaction_and_roles.items():
                self.embed.description += f"{emoji_id} - <@&{role_id}>\n"

            self.unique_selector = nextcord.ui.Select(
                placeholder="Только одна выбранная роль",
                options=[
                    nextcord.SelectOption(label="Да", value="1", default=self.unique),
                    nextcord.SelectOption(
                        label="Нет", value="0", default=not self.unique
                    ),
                ],
            )
            self.unique_set = True
            self.add_item(self.unique_selector)

            self.single_use_selector = nextcord.ui.Select(
                placeholder="Однократное использование",
                options=[
                    nextcord.SelectOption(
                        label="Да", value="1", default=self.single_use
                    ),
                    nextcord.SelectOption(
                        label="Нет", value="0", default=not self.single_use
                    ),
                ],
            )
            self.single_use_set = True
            self.add_item(self.single_use_selector)

            self.send_button: nextcord.ui.Button = nextcord.ui.Button(
                style=nextcord.ButtonStyle.green, label="Сохранить", row=0
            )
            self.add_item(self.send_button)
        else:
            self.unique = False
            self.single_use = False
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
                style=nextcord.ButtonStyle.green,
                label="Сохранить",
                disabled=True,
                row=0,
            )
            self.add_item(self.send_button)

        self.cancel_button: nextcord.ui.Button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.red, label="Отмена", row=0
        )
        self.add_item(self.cancel_button)

    async def interaction_check(self, interaction: nextcord.Interaction):
        if self.author == interaction.user:
            match interaction.data["custom_id"]:
                case self.colour_button.custom_id:
                    request_message = await interaction.send(
                        "Укажите цвет в формате hex, или напишите любой текст для выбора случайного"
                    )
                    try:
                        message: nextcord.Message = await self.bot.wait_for(
                            "message",
                            check=lambda msg: msg.author == self.author
                            and msg.channel == self.original_channel,
                            timeout=300.0,
                        )
                    except TimeoutError:
                        await request_message.delete()
                        return
                    self.embed.colour = parse_color(message.content)
                    if self.preview_message is not None:
                        await self.preview_message.edit(embed=self.embed)
                    await request_message.delete()
                    await message.delete()
                case self.title_button.custom_id:
                    request_message = await interaction.send("Укажите заголовок блока")
                    try:
                        message: nextcord.Message = await self.bot.wait_for(
                            "message",
                            check=lambda msg: msg.author == self.author
                            and msg.channel == self.original_channel,
                            timeout=300.0,
                        )
                    except TimeoutError:
                        await request_message.delete()
                        return
                    self.embed.title = message.content
                    if self.preview_message is not None:
                        await self.preview_message.edit(embed=self.embed)
                    if self.send_button.disabled:
                        self.send_button.disabled = False
                        await self.control_message.edit(view=self)
                    await request_message.delete()
                    await message.delete()
                case self.text_button.custom_id:
                    request_message = await interaction.send(
                        "Укажите текст внутри блока"
                    )
                    try:
                        message: nextcord.Message = await self.bot.wait_for(
                            "message",
                            check=lambda msg: msg.author == self.author
                            and msg.channel == self.original_channel,
                            timeout=300.0,
                        )
                    except TimeoutError:
                        await request_message.delete()
                        return
                    self.text = message.content
                    if self.embed.title == "Предпросмотр":
                        self.embed.title = ""
                    self.embed.description = self.text + (
                        "\n\n" if self.text != "" else ""
                    )
                    for emoji_id, role_id in self.reaction_and_roles.items():
                        self.embed.description += f"{emoji_id} - <@&{role_id}>\n"
                    if self.preview_message is not None:
                        await self.preview_message.edit(embed=self.embed)
                    if self.send_button.disabled:
                        self.send_button.disabled = False
                        await self.control_message.edit(view=self)
                    await request_message.delete()
                    await message.delete()
                case self.icon_button.custom_id:
                    request_message = await interaction.send("Укажите иконку блока")
                    try:
                        message: nextcord.Message = await self.bot.wait_for(
                            "message",
                            check=lambda msg: msg.author == self.author
                            and msg.channel == self.original_channel,
                            timeout=300.0,
                        )
                    except TimeoutError:
                        await request_message.delete()
                        return
                    if not url(message.content):
                        await request_message.delete()
                        await message.delete()
                        return
                    self.embed.set_thumbnail(url=message.content)
                    if self.preview_message is not None:
                        await self.preview_message.edit(embed=self.embed)
                    if self.send_button.disabled:
                        self.send_button.disabled = False
                        await self.control_message.edit(view=self)
                    await request_message.delete()
                    await message.delete()
                case self.message_button.custom_id:
                    request_message = await interaction.send(
                        "Укажите сообщение над блоком"
                    )
                    try:
                        message: nextcord.Message = await self.bot.wait_for(
                            "message",
                            check=lambda msg: msg.author == self.author
                            and msg.channel == self.original_channel,
                            timeout=300.0,
                        )
                    except TimeoutError:
                        await request_message.delete()
                        return
                    self.message_text = message.content
                    content_message = (
                        f"**Только одна выбранная роль:** {'Да' if self.unique else 'Нет'}\n"
                        + f"**Однократное использование:** {'Да' if self.single_use else 'Нет'}"
                        + (
                            "\n\n" + self.message_text
                            if self.message_text != ""
                            else ""
                        )
                    )
                    if self.preview_message is not None:
                        await self.preview_message.edit(
                            content=content_message, embed=self.embed
                        )
                    if self.send_button.disabled:
                        self.send_button.disabled = False
                        await self.control_message.edit(view=self)
                    await request_message.delete()
                    await message.delete()
                case self.add_button.custom_id:
                    request_emoji_message = await interaction.send("Укажите эмозди")
                    try:
                        emoji_message: nextcord.Message = await self.bot.wait_for(
                            "message",
                            check=lambda msg: msg.author == self.author
                            and msg.channel == self.original_channel,
                            timeout=300.0,
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
                            timeout=300.0,
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
                    self.embed.description = self.text + (
                        "\n\n" if self.text != "" else ""
                    )
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
                            timeout=300.0,
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

                    self.embed.description = self.text + (
                        "\n\n" if self.text != "" else ""
                    )
                    for emoji_id, role_id in self.reaction_and_roles.items():
                        self.embed.description += f"{emoji_id} - <@&{role_id}>\n"

                    if self.preview_message is not None:
                        await self.preview_message.edit(embed=self.embed)
                    await request_emoji_message.delete()
                    await emoji_message.delete()
                case self.send_button.custom_id:
                    if self.reaction_and_roles == {}:
                        await interaction.send("Не добавлено **ни одного** эмодзи")

                    if self.message is None:
                        self.message = await self.channel.send(
                            content=self.message_text, embed=self.embed
                        )
                    else:
                        await self.message.clear_reactions()

                    if self.edit_existing:
                        await self.message.edit(
                            content=self.message_text, embed=self.embed
                        )

                    for emoji_id in self.reaction_and_roles:
                        try:
                            await self.message.add_reaction(emoji_id)
                        except:
                            continue

                    try:
                        await self.control_message.delete()
                        await self.preview_message.delete()
                    except:
                        pass

                    self.bot.database.add_reaction_roles_info(
                        self.message.id,
                        self.channel.id,
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
                        + f"**Однократное использование:** {'Да' if self.single_use else 'Нет'}"
                        + (
                            "\n\n" + self.message_text
                            if self.message_text != ""
                            else ""
                        )
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
                            timeout=300.0,
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
                        + f"**Однократное использование:** {'Да' if self.single_use else 'Нет'}"
                        + (
                            "\n\n" + self.message_text
                            if self.message_text != ""
                            else ""
                        )
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


class VerifyReactionRolesSetup(nextcord.ui.View):
    def __init__(
        self,
        author: nextcord.Member,
        bot,
        channel: nextcord.TextChannel,
    ):
        super().__init__(timeout=1200.0)
        self.bot = bot
        self.author: nextcord.Member = author
        self.control_message: Optional[nextcord.Message] = None
        self.preview_message: Optional[nextcord.Message] = None
        self.original_channel: Optional[nextcord.TextChannel] = None
        self.channel = channel

        self.add_button = nextcord.ui.Button(label="Добавить", row=0)
        self.add_item(self.add_button)

        self.delete_button = nextcord.ui.Button(label="Удалить", row=0)
        self.add_item(self.delete_button)

        self.text = ""
        self.message_text = ""

        self.colour_button = nextcord.ui.Button(label="Цвет", row=1)
        self.title_button = nextcord.ui.Button(label="Заголовок", row=1)
        self.text_button = nextcord.ui.Button(label="Текст", row=1)
        self.icon_button = nextcord.ui.Button(label="Иконка", row=1)
        self.message_button = nextcord.ui.Button(label="Сообщение", row=1)
        self.add_item(self.colour_button)
        self.add_item(self.title_button)
        self.add_item(self.text_button)
        self.add_item(self.icon_button)
        self.add_item(self.message_button)

        self.embed = nextcord.Embed(title="Предпросмотр")
        self.reaction_and_roles = {}
        self.unique = True
        self.single_use = True

        self.send_button: nextcord.ui.Button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.green,
            label="Сохранить",
            disabled=True,
            row=0,
        )
        self.add_item(self.send_button)

        self.cancel_button: nextcord.ui.Button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.red, label="Отмена", row=0
        )
        self.add_item(self.cancel_button)

    async def interaction_check(self, interaction: nextcord.Interaction):
        if self.author == interaction.user:
            match interaction.data["custom_id"]:
                case self.colour_button.custom_id:
                    request_message = await interaction.send(
                        "Укажите цвет в формате hex, или напишите любой текст для выбора случайного"
                    )
                    try:
                        message: nextcord.Message = await self.bot.wait_for(
                            "message",
                            check=lambda msg: msg.author == self.author
                            and msg.channel == self.original_channel,
                            timeout=300.0,
                        )
                    except TimeoutError:
                        await request_message.delete()
                        return
                    self.embed.colour = parse_color(message.content)
                    if self.preview_message is not None:
                        await self.preview_message.edit(embed=self.embed)
                    await request_message.delete()
                    await message.delete()
                case self.title_button.custom_id:
                    request_message = await interaction.send("Укажите заголовок блока")
                    try:
                        message: nextcord.Message = await self.bot.wait_for(
                            "message",
                            check=lambda msg: msg.author == self.author
                            and msg.channel == self.original_channel,
                            timeout=300.0,
                        )
                    except TimeoutError:
                        await request_message.delete()
                        return
                    self.embed.title = message.content
                    if self.preview_message is not None:
                        await self.preview_message.edit(embed=self.embed)
                    if self.send_button.disabled:
                        self.send_button.disabled = False
                        await self.control_message.edit(view=self)
                    await request_message.delete()
                    await message.delete()
                case self.text_button.custom_id:
                    request_message = await interaction.send(
                        "Укажите текст внутри блока"
                    )
                    try:
                        message: nextcord.Message = await self.bot.wait_for(
                            "message",
                            check=lambda msg: msg.author == self.author
                            and msg.channel == self.original_channel,
                            timeout=300.0,
                        )
                    except TimeoutError:
                        await request_message.delete()
                        return
                    self.text = message.content
                    if self.embed.title == "Предпросмотр":
                        self.embed.title = ""
                    self.embed.description = self.text + (
                        "\n\n" if self.text != "" else ""
                    )
                    for emoji_id, role_id in self.reaction_and_roles.items():
                        self.embed.description += f"{emoji_id} - <@&{role_id}>\n"
                    if self.preview_message is not None:
                        await self.preview_message.edit(embed=self.embed)
                    if self.send_button.disabled:
                        self.send_button.disabled = False
                        await self.control_message.edit(view=self)
                    await request_message.delete()
                    await message.delete()
                case self.icon_button.custom_id:
                    request_message = await interaction.send("Укажите иконку блока")
                    try:
                        message: nextcord.Message = await self.bot.wait_for(
                            "message",
                            check=lambda msg: msg.author == self.author
                            and msg.channel == self.original_channel,
                            timeout=300.0,
                        )
                    except TimeoutError:
                        await request_message.delete()
                        return
                    if not url(message.content):
                        await request_message.delete()
                        await message.delete()
                        return
                    self.embed.set_thumbnail(url=message.content)
                    if self.preview_message is not None:
                        await self.preview_message.edit(embed=self.embed)
                    if self.send_button.disabled:
                        self.send_button.disabled = False
                        await self.control_message.edit(view=self)
                    await request_message.delete()
                    await message.delete()
                case self.message_button.custom_id:
                    request_message = await interaction.send(
                        "Укажите сообщение над блоком"
                    )
                    try:
                        message: nextcord.Message = await self.bot.wait_for(
                            "message",
                            check=lambda msg: msg.author == self.author
                            and msg.channel == self.original_channel,
                            timeout=300.0,
                        )
                    except TimeoutError:
                        await request_message.delete()
                        return
                    self.message_text = message.content
                    if self.preview_message is not None:
                        await self.preview_message.edit(
                            content=self.message_text, embed=self.embed
                        )
                    if self.send_button.disabled:
                        self.send_button.disabled = False
                        await self.control_message.edit(view=self)
                    await request_message.delete()
                    await message.delete()
                case self.add_button.custom_id:
                    request_emoji_message = await interaction.send("Укажите эмозди")
                    try:
                        emoji_message: nextcord.Message = await self.bot.wait_for(
                            "message",
                            check=lambda msg: msg.author == self.author
                            and msg.channel == self.original_channel,
                            timeout=300.0,
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
                            timeout=300.0,
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
                    self.embed.description = self.text + (
                        "\n\n" if self.text != "" else ""
                    )

                    if self.send_button.disabled:
                        self.send_button.disabled = True
                        if self.control_message is not None:
                            await self.control_message.edit(view=self)
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
                            timeout=300.0,
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

                    self.embed.description = self.text + (
                        "\n\n" if self.text != "" else ""
                    )
                    for emoji_id, role_id in self.reaction_and_roles.items():
                        self.embed.description += f"{emoji_id} - <@&{role_id}>\n"

                    if self.reaction_and_roles == {}:
                        self.send_button.disabled = False
                        if self.control_message is not None:
                            await self.control_message.edit(view=self)

                    if self.preview_message is not None:
                        await self.preview_message.edit(embed=self.embed)
                    await request_emoji_message.delete()
                    await emoji_message.delete()
                case self.send_button.custom_id:
                    if self.reaction_and_roles == {}:
                        await interaction.send("Не добавлено **ни одного** эмодзи")

                    message = await self.channel.send(
                        content=self.message_text, embed=self.embed
                    )

                    for emoji_id in self.reaction_and_roles:
                        try:
                            await message.add_reaction(emoji_id)
                        except:
                            continue

                    try:
                        await self.control_message.delete()
                        await self.preview_message.delete()
                    except:
                        pass

                    self.bot.database.add_verify_roles_info(
                        message.id,
                        self.channel.id,
                        self.author.id,
                        self.reaction_and_roles,
                    )

                    await self.original_channel.send(
                        "Сообщение успешно отправлено! "
                        + "Для удаления воспользуйтесь методом для обычных ReactionRoles"
                    )
                    self.stop()
                case self.cancel_button.custom_id:
                    await self.on_timeout()
                    self.stop()
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
