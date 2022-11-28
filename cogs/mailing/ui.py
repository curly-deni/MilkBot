from typing import Optional

import nextcord
from validators import url


def parse_color(content: str):
    if content.startswith("#"):
        try:
            return int(content[1:], 16)
        except:
            return nextcord.Colour.random()
    else:
        return nextcord.Colour.random()


class EmbedSender(nextcord.ui.View):
    def __init__(
        self,
        author: nextcord.Member,
        bot,
        channel: nextcord.TextChannel,
        message: Optional[nextcord.Message],
    ):
        super().__init__(timeout=1200.0)
        self.bot = bot
        self.author: nextcord.Member = author
        self.control_message: Optional[nextcord.Message] = None
        self.preview_message: Optional[nextcord.Message] = None
        self.content_message = ""
        self.original_channel: Optional[nextcord.TextChannel] = None
        self.channel = channel
        self.message = message

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
                            timeout=300.0,
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
                case self.image_button.custom_id:
                    request_message = await interaction.send("Укажите изображение")
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
                            timeout=300.0,
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
                    await interaction.response.defer()
                    if self.message is None:
                        self.message = await self.channel.send(
                            self.content_message, embed=self.embed
                        )
                    else:
                        await self.message.edit(
                            content=self.content_message, embed=self.embed
                        )
                    await interaction.followup.send("Сообщение успешно отправлено!")
                    self.bot.database.add_embed_info(
                        self.message.id, self.channel.id, self.author.id
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
