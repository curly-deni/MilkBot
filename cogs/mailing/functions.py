import asyncio
import traceback
from datetime import datetime, timedelta
from random import choice
from typing import Optional, Union

import nextcord
import vk_api
from base.base_cog import MilkCog
from nextcord.ext import commands, tasks

from .ui import EmbedSender


def hex_to_rgb(hex: str) -> list[int]:
    rgb: list = []
    for i in (0, 2, 4):
        decimal: int = int(hex[i : i + 2], 16)
        rgb.append(decimal)
    return list(rgb)


class Mailing(MilkCog, name="Рассылка"):
    """Рассылка различных сообщений для администраторов"""

    COG_EMOJI: str = "✉"

    def __init__(self, bot):

        self.bot = bot
        self.anime_horo_send.start()

    @tasks.loop(hours=24)
    async def anime_horo_send(self):

        vk = vk_api.VkApi(token=self.bot.settings["vk_token"]).get_api()

        posts: list = vk.wall.get(domain="aniscope", count=100)["items"]
        finded_text = []
        embed_list = []
        channels: list[list] = self.bot.database.get_all_horo()
        for post in posts:
            text: Union[list, str] = post["text"]
            if isinstance(text, list):
                text = "\n".join(text)
            if (
                text.lower().find("гороскоп") != -1
                and datetime.utcfromtimestamp(post["date"]).date()
                == (datetime.now() - timedelta(days=1)).date()
            ):
                photos: list[dict] = post["attachments"][0]["photo"]["sizes"]
                max_height = 0
                for photo in photos:
                    max_height: int = max(max_height, photo["height"])
                for photo in photos:
                    if photo["height"] == max_height:
                        url: str = photo["url"]
                        if not isinstance(text, list):
                            text = text.split("\n")
                        for txt in text:
                            if txt == "" or txt == " ":
                                text.remove(txt)

                        if len(text) != 5:
                            continue

                        if text not in finded_text:
                            embed = nextcord.Embed(description=text[2])
                            embed.colour = nextcord.Colour.blurple()
                            embed.add_field(name=text[1], value=f"{text[3]}\n{text[4]}")
                            embed.set_footer(
                                text=f'{text[0]}\nГороскоп автоматически взят с группы ВК "Аниме гороскопы"'
                            )
                            embed.set_image(url=url)
                            embed_list.append(embed)
                            finded_text.append(text)
                            break
            if len(embed_list) == 12:
                break
        if len(embed_list) != 12:
            return
        for channel in channels:
            try:
                channel_object: nextcord.TextChannel = self.bot.get_channel(channel[0])
                for embed in embed_list:
                    await channel_object.send(embed=embed)
                if channel[1] and embed_list:
                    await channel_object.send(
                        " ".join(f"<@&{role}>" for role in channel[1])
                    )
            except:
                continue

    @anime_horo_send.before_loop
    async def before_anime_horo_send(self):
        hour: int = 0
        minute: int = 15
        await self.bot.wait_until_ready()
        now = datetime.now()
        future = datetime(now.year, now.month, now.day, hour, minute)
        if now.hour >= hour and now.minute > minute:
            future += timedelta(days=1)
        await asyncio.sleep((future - now).seconds)

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        if message.channel.id == 876541671997837312:
            await message.add_reaction("✅")
            await message.add_reaction("❌")

    @commands.Cog.listener()
    async def on_member_remove(self, member: nextcord.Member):

        guild_info = self.bot.database.get_guild_info(member.guild.id)
        if not guild_info.verifed_user_leave_notify:
            return

        member_roles = [
            role for role in member.roles if role != member.guild.default_role
        ]
        if not member_roles:
            return

        try:
            channel = self.bot.get_channel(guild_info.verifed_user_leave_notify_channel)
            phrase = (
                choice(guild_info.verifed_user_leave_notify_phrases)
                .replace("user_mention", member.mention)
                .replace("user_name", member.name)
            )
            await channel.send(phrase)
        except Exception as error:
            return await member.guild.owner.send(
                "При отправке уведомления о уходе пользователя с сервера в чат возникла ошибка:\n"
                + "\n".join(traceback.format_exception(error))
            )

    @MilkCog.slash_command(permission="editor")
    async def send(self, interaction: nextcord.Interaction):
        ...

    @send.subcommand(
        name="message", description="Отправка текстового сообщения в канал"
    )
    async def send_message(
        self,
        interaction: nextcord.Interaction,
        channel: Optional[nextcord.TextChannel] = nextcord.SlashOption(
            name="канал", required=True
        ),
        message: Optional[str] = nextcord.SlashOption(name="сообщение", required=True),
    ):

        await interaction.response.defer(ephemeral=True)

        try:
            await channel.send(message)
        except Exception as e:
            return await interaction.followup.send(str(e))
        return await interaction.followup.send("Успешно")

    @send.subcommand(
        name="embed",
        description="Интерактивное создание Embed-сообщений",
    )
    async def embed_create(
        self,
        interaction: nextcord.Interaction,
        channel: Optional[nextcord.TextChannel] = nextcord.SlashOption(
            name="канал", required=True
        ),
        edit_existing: bool = nextcord.SlashOption(
            name="редактировать_сообщение",
            description="Необходимо ли отредактировать сообщение (бот должен быть автором сообщения)",
            choices={
                "Да": True,
                "Нет": False,
            },
            required=True,
        ),
        id: str = nextcord.SlashOption(
            name="id",
            description="ID-сообщения, в котором находится Reaction Roles",
            required=True,
        ),
    ):
        await interaction.response.defer()
        message = None
        if edit_existing:
            try:
                message = await channel.fetch_message(int(id))
            except:
                await interaction.followup.send(f"Не найдено сообщения с ID {id}")
                return
            if message is None:
                await interaction.followup.send(f"Не найдено сообщения с ID {id}")
                return
            else:
                if message.author != self.bot.user:
                    await interaction.followup.send(
                        f"Бот не является автором данного сообщения, создаем новое"
                    )
                    return
                else:
                    message_info = self.bot.database.get_embed_info(
                        message.id, channel.id
                    )
                    if message_info is None:
                        await interaction.followup.send(
                            f"Данное сообщение не является редактируемым, создаем новое сообщение"
                        )
                        return
                    elif message_info.author_id != interaction.user.id:
                        await interaction.followup.send(
                            "Вы не являетесь автором данного сообщения, создаем новое сообщение"
                        )
                        return

        view = EmbedSender(interaction.user, self.bot, channel, message)
        control_message = await interaction.followup.send(view=view)
        preview_message = await interaction.followup.send(embed=view.embed)
        view.preview_message = preview_message
        view.control_message = control_message
        view.original_channel = interaction.channel
        await view.wait()


def setup(bot):
    bot.add_cog(Mailing(bot))
