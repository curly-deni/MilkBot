import nextcord
from nextcord.ext import commands, tasks
from typing import Optional

import asyncio
from datetime import datetime, timedelta
import vk_api

from modules.checkers import check_moderator_permission, app_check_moderator_permission
from typing import Callable, TypeVar, Union
from modules.utils import hex_to_rgb

T = TypeVar("T")


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
                if channel[1]:
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
        description="Отправка Embed-сообщения из таблицы",
    )
    async def embed_send(self, interaction: nextcord.Interaction):
        if interaction.guild is None:
            return await interaction.send("Вы на находитесь на сервере!")
        await interaction.response.defer(ephemeral=True)

        if not app_check_moderator_permission(interaction, self.bot):
            return await interaction.followup.send("Недостаточно прав!", ephemeral=True)

        embeds: list[list] = self.bot.tables.get_embeds(interaction.guild.id)

        for embed in embeds:
            if embed[0] != "":
                channel: nextcord.TextChannel = self.bot.get_channel(int(embed[1]))
                emb: nextcord.Embed = nextcord.Embed(description=embed[6])

                if embed[2] != "None":
                    emb.title = embed[2]

                if embed[3] == "guild_icon" and interaction.guild.icon:
                    emb.set_thumbnail(url=interaction.guild.icon.url)

                elif embed[3].lower() != "none":
                    emb.set_thumbnail(url=embed[3])

                if embed[4].lower() != "none":
                    emb.set_image(url=embed[4])

                if embed[7] != "":
                    emb.colour = nextcord.Colour.from_rgb(*hex_to_rgb(embed[5][1:]))

                if embed[0] != "None":
                    message: nextcord.Message = await channel.fetch_message(
                        int(embed[0])
                    )
                    await message.edit(embed=emb)
                else:
                    message: nextcord.Message = await channel.send(embed=emb)
                self.bot.tables.update_embed(interaction.guild.id, message.id, embed[7])
                await interaction.followup.send(
                    f"{interaction.user.mention}, успешно отправлено!"
                )

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

    async def create_cancel_msg(
        self,
        ctx: commands.Context,
        name: str,
        on_cancel: Callable[[], T],
        on_message: Callable[[nextcord.Message], T],
    ) -> T:
        color_help = await ctx.send(name)
        await color_help.add_reaction("❌")

        async def get_reaction():
            def check(reaction: nextcord.Reaction, user: nextcord.User):
                return reaction.emoji in ["❌"] and user == ctx.message.author

            reaction, user = await self.bot.wait_for("reaction_add", check=check)
            return on_cancel()

        async def get_message() -> int:
            def check(message: nextcord.Message):
                return message.author == ctx.author and message.channel == ctx.channel

            msg = await self.bot.wait_for("message", check=check)
            color = on_message(msg)
            await msg.delete()
            return color

        tasks = [get_message(), get_reaction()]
        finished, unfinished = await asyncio.wait(
            tasks, return_when=asyncio.FIRST_COMPLETED
        )

        result = finished.pop().result()
        for task in unfinished:
            task.cancel()
        await asyncio.wait(unfinished)
        await color_help.delete()
        return result

    @commands.command(brief="Интерактивное создание Embed-сообщений", aliases=["embed"])
    @commands.check(check_moderator_permission)
    @commands.guild_only()
    async def embed_создать(self, ctx: commands.Context):
        def parse_color(content: str):
            if content.startswith("#"):
                try:
                    return int(content[1:], 16)
                except:
                    return nextcord.Colour.random()
            else:
                return nextcord.Colour.random()

        color = await self.create_cancel_msg(
            ctx,
            "Напишите цвет, например, #91e1fe, или нажмите на крестик для выбора случайного цвета.",
            lambda: nextcord.Colour.random(),
            lambda msg: parse_color(msg.content),
        )

        title = await self.create_cancel_msg(
            ctx, "Название Embed-блока.", lambda: "", lambda msg: msg.content
        )
        description = await self.create_cancel_msg(
            ctx,
            "Напишите текст внутри Embed-блока.",
            lambda: "",
            lambda msg: msg.content,
        )
        text = await self.create_cancel_msg(
            ctx, "Напишите текст над Embed-блоком.", lambda: "", lambda msg: msg.content
        )
        big_image = await self.create_cancel_msg(
            ctx,
            "Отправьте ссылку с основным изображением",
            lambda: "",
            lambda msg: msg.content,
        )
        thumbnail = await self.create_cancel_msg(
            ctx,
            "Отправьте ссылку с изображением в правом углу Embed-блока",
            lambda: "",
            lambda msg: msg.content,
        )
        footer = await self.create_cancel_msg(
            ctx,
            "Напишите текст под изображением (Footer).",
            lambda: "",
            lambda msg: msg.content,
        )

        embed = nextcord.Embed(title=title, description=description, colour=color)
        embed.set_footer(text=footer)
        embed.set_image(url=big_image)
        embed.set_thumbnail(url=thumbnail)
        embed_preview = await ctx.send(
            "```Нажмите на ✅ для выбора чата или нажмите на ❌ для отмены.```\n" + text,
            embed=embed,
        )
        await embed_preview.add_reaction("✅")
        await embed_preview.add_reaction("❌")
        reaction, user = await self.bot.wait_for(
            "reaction_add",
            check=lambda reaction, user: reaction.emoji in ["✅", "❌"]
            and user == ctx.message.author,
        )
        if reaction.emoji == "✅":

            def check(message):
                return message.author == ctx.author and message.channel == ctx.channel

            embed_help = await ctx.send("Напишите чат для отправки сообщения.")
            channelid = await self.bot.wait_for("message", check=check)
            channelid.content = (
                channelid.content.replace("#", "").replace("<", "").replace(">", "")
            )
            channel = self.bot.get_channel(int(channelid.content))
            embed = nextcord.Embed(title=title, description=text, colour=color)
            embed.set_footer(text=footer)
            embed.set_image(url=big_image)
            embed.set_thumbnail(url=thumbnail)
            await channel.send(text, embed=embed)
            await embed_preview.delete()
            await embed_help.delete()
            await channelid.delete()
        if reaction.emoji == "❌":
            await embed_preview.delete()
            return


def setup(bot):
    bot.add_cog(Mailing(bot))
