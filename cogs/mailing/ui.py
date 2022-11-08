import nextcord
from validators import url
from typing import Optional
from modules.utils import create_cancel_msg_without_ctx


def parse_color(content: str):
    if content.startswith("#"):
        try:
            return int(content[1:], 16)
        except:
            return nextcord.Colour.random()
    else:
        return nextcord.Colour.random()


class EmbedSender(nextcord.ui.View):
    def __init__(self, author: nextcord.Member, bot):
        super().__init__(timeout=240.0)
        self.bot = bot
        self.author: nextcord.Member = author
        self.control_message: Optional[nextcord.Message] = None
        self.preview_message: Optional[nextcord.Message] = None
        self.content_message = ""
        self.original_channel: Optional[nextcord.TextChannel] = None

        self.embed = nextcord.Embed(title="Предпросмотр")

        self.colour_button = nextcord.ui.Button(label="Цвет")
        self.add_item(self.colour_button)

        self.title_button = nextcord.ui.Button(label="Заголовок")
        self.add_item(self.title_button)

        self.text_button = nextcord.ui.Button(label="Текст")
        self.add_item(self.text_button)

        self.footer_button = nextcord.ui.Button(label="Footer")
        self.add_item(self.footer_button)

        self.icon_button = nextcord.ui.Button(label="Иконка")
        self.add_item(self.icon_button)

        self.image_button = nextcord.ui.Button(label="Изображение")
        self.add_item(self.image_button)

        self.message_button = nextcord.ui.Button(label="Сообщение")
        self.add_item(self.message_button)

        self.send_button: nextcord.ui.Button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.green, label="Отправить", disabled=True
        )
        self.add_item(self.send_button)

        self.cancel_button: nextcord.ui.Button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.red, label="Отмена"
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
                            timeout=60.0,
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
                            timeout=60.0,
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
                            timeout=60.0,
                        )
                    except TimeoutError:
                        await request_message.delete()
                        return
                    self.embed.description = message.content
                    if self.preview_message is not None:
                        await self.preview_message.edit(embed=self.embed)
                    if self.send_button.disabled:
                        self.send_button.disabled = False
                        await self.control_message.edit(view=self)
                    await request_message.delete()
                    await message.delete()
                case self.footer_button.custom_id:
                    request_message = await interaction.send("Укажите футер")
                    try:
                        message: nextcord.Message = await self.bot.wait_for(
                            "message",
                            check=lambda msg: msg.author == self.author
                            and msg.channel == self.original_channel,
                            timeout=60.0,
                        )
                    except TimeoutError:
                        await request_message.delete()
                        return
                    self.embed.set_footer(text=message.content)
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
                            timeout=60.0,
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
                case self.image_button.custom_id:
                    request_message = await interaction.send("Укажите изображение")
                    try:
                        message: nextcord.Message = await self.bot.wait_for(
                            "message",
                            check=lambda msg: msg.author == self.author
                            and msg.channel == self.original_channel,
                            timeout=60.0,
                        )
                    except TimeoutError:
                        await request_message.delete()
                        return
                    if not url(message.content):
                        await request_message.delete()
                        await message.delete()
                        return
                    self.embed.set_image(url=message.content)
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
                            timeout=60.0,
                        )
                    except TimeoutError:
                        await request_message.delete()
                        return
                    self.content_message = message.content
                    if self.preview_message is not None:
                        await self.preview_message.edit(
                            content=self.content_message, embed=self.embed
                        )
                    if self.send_button.disabled:
                        self.send_button.disabled = False
                        await self.control_message.edit(view=self)
                    await request_message.delete()
                    await message.delete()
                case self.send_button.custom_id:
                    status_messages = []
                    response = await interaction.send("Starting up")
                    await response.delete()

                    channel: Optional[nextcord.TextChannel] = None
                    channel_id: Optional[str] = await create_cancel_msg_without_ctx(
                        self.bot,
                        self.author,
                        self.original_channel,
                        "Введите ID канала, если хотите отредактировать сообщение, иначе нажмите на крестик",
                        lambda: None,
                        lambda msg: msg.content,
                    )

                    if channel_id is not None:
                        if not channel_id.isdigit():
                            status_messages.append(
                                await self.original_channel.send(
                                    f"Неверно указан канал, создаем новое сообщение!"
                                )
                            )
                        else:
                            channel = self.bot.get_channel(int(channel_id))
                            if channel is not None:
                                status_messages.append(
                                    await self.original_channel.send(
                                        f"Выбран канал **{channel.name}** ({channel.id})"
                                    )
                                )
                            else:
                                status_messages.append(
                                    await self.original_channel.send(
                                        f"Канал с ID {channel_id} не обнаружен, создаем новое сообщение!"
                                    )
                                )

                    message: Optional[nextcord.Message] = None
                    if channel is not None:
                        message_id: Optional[str] = await create_cancel_msg_without_ctx(
                            self.bot,
                            self.author,
                            self.original_channel,
                            "Введите ID сообщения",
                            lambda: None,
                            lambda msg: msg.content,
                        )
                        if message_id is None:
                            status_messages.append(
                                await self.original_channel.send(
                                    f"Не указан ID сообщения, создаем новое сообщение"
                                )
                            )
                        else:
                            if not message_id.isdigit():
                                status_messages.append(
                                    await self.original_channel.send(
                                        "Неверно указан ID сообшения, создаем новое сообщение"
                                    )
                                )
                            else:
                                message = await channel.fetch_message(int(message_id))
                                if message is None:
                                    status_messages.append(
                                        await self.original_channel.send(
                                            f"Сообщение с ID {message_id} в канале {channel_id} не обнаружено, создаем новое"
                                        )
                                    )
                                else:
                                    if message.author != self.bot.user:
                                        status_messages.append(
                                            await self.original_channel.send(
                                                f"Бот не является автором данного сообщения, создаем новое"
                                            )
                                        )
                                    else:
                                        message_info = self.bot.database.get_embed_info(
                                            message.id, channel.id
                                        )
                                        if message_info is None:
                                            message = None
                                            status_messages.append(
                                                await self.original_channel.send(
                                                    f"Данное сообщение не является редактируемым, создаем новое сообщение"
                                                )
                                            )
                                        elif message_info.author_id != self.author.id:
                                            message = None
                                            status_messages.append(
                                                await self.original_channel.send(
                                                    "Вы не являетесь автором данного сообщения, создаем новое сообщение"
                                                )
                                            )
                                        else:
                                            status_messages.append(
                                                await self.original_channel.send(
                                                    "Сообщение выбрано!"
                                                )
                                            )

                    if message is None:
                        embed_help = await self.original_channel.send(
                            "Напишите ID чата для отправки сообщения."
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
                        channel = self.bot.get_channel(int(channel_id.content))
                        message = await channel.send(
                            self.content_message, embed=self.embed
                        )
                        await channel_id.delete()
                        await embed_help.delete()
                    else:
                        await message.edit(
                            content=self.content_message, embed=self.embed
                        )
                    await self.control_message.delete()
                    await self.preview_message.delete()
                    for i in status_messages:
                        try:
                            await i.delete()
                        except:
                            continue

                    self.bot.database.add_embed_info(
                        message.id, channel.id, self.author.id
                    )
                    await self.original_channel.send("Сообщение успешно отправлено!")
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
