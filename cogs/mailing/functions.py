import nextcord
from nextcord.ext import commands, tasks
from typing import Optional

import asyncio
from datetime import datetime, timedelta
import vk_api

from modules.checkers import check_moderator_permission, app_check_moderator_permission
from typing import Union
from .ui import EmbedSender
from modules.utils import create_cancel_msg


def hex_to_rgb(hex: str) -> list[int]:
    rgb: list = []
    for i in (0, 2, 4):
        decimal: int = int(hex[i : i + 2], 16)
        rgb.append(decimal)
    return list(rgb)


class Mailing(commands.Cog, name="Рассылка"):
    """Рассылка различных сообщений для администраторов"""

    COG_EMOJI: str = "✉"

    def __init__(self, bot):

        self.bot = bot
        if self.bot.bot_type != "helper":
            self.anime_horo_send.start()

    @tasks.loop(hours=24)
    async def anime_horo_send(self):

        vk: vk_api.VkApiMethod = vk_api.VkApi(
            token=self.bot.settings["vk_token"]
        ).get_api()

        posts: list = vk.wall.get(domain="aniscope", count=100)["items"]
        find_correct_posts: int = 0
        correct_posts_list: list = []
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
                max_height: int = 0
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
                        if [url, text] not in correct_posts_list:
                            correct_posts_list.append([url, text])
                            break
                find_correct_posts += 1
            if find_correct_posts == 12:
                break

        await asyncio.sleep(5)
        channels: list[list] = self.bot.database.get_all_horo()
        embeds: list[nextcord.Embed] = []
        for element in correct_posts_list:
            emb: nextcord.Embed = nextcord.Embed(description=element[1][2])
            emb.colour = nextcord.Colour.blurple()
            emb.add_field(name=element[1][1], value=f"{element[1][3]}\n{element[1][4]}")
            emb.set_footer(
                text=f'{element[1][0]}\nГороскоп автоматически взят с группы ВК "Аниме гороскопы"'
            )
            emb.set_image(url=element[0])
            embeds.append(emb)

        for channel in channels:
            try:
                channel_object: nextcord.TextChannel = self.bot.get_channel(channel[0])
                for emb in embeds:
                    await channel_object.send(embed=emb)
                if channel[1] and embeds:
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

    @nextcord.slash_command(
        guild_ids=[],
        force_global=True,
        description="Отправка текстового сообщения в канал",
    )
    async def send(
        self,
        interaction: nextcord.Interaction,
        канал: Optional[nextcord.abc.GuildChannel] = nextcord.SlashOption(
            required=True
        ),
        сообщение: Optional[str] = nextcord.SlashOption(required=True),
    ):
        if interaction.guild is None:
            return await interaction.send("Вы на находитесь на сервере!")
        await interaction.response.defer(ephemeral=True)

        if not app_check_moderator_permission(interaction, self.bot):
            return await interaction.followup.send("Недостаточно прав!", ephemeral=True)

        channel = канал
        message = сообщение

        if not isinstance(channel, nextcord.TextChannel):
            return

        try:
            await channel.send(message)
        except Exception as e:
            return await interaction.followup.send(str(e))
        return await interaction.followup.send("Успешно")

    @commands.command(
        brief="Интерактивное создание Embed-сообщений",
        aliases=["embed_создать", "embed", "создать_embed", "create_embed"],
    )
    @commands.check(check_moderator_permission)
    @commands.guild_only()
    async def embed_create(self, ctx: commands.Context):
        view = EmbedSender(ctx.author, self.bot)
        control_message = await ctx.send(view=view)
        preview_message = await ctx.send(embed=view.embed)
        view.preview_message = preview_message
        view.control_message = control_message
        view.original_channel = ctx.channel
        await view.wait()


def setup(bot):
    bot.add_cog(Mailing(bot))
