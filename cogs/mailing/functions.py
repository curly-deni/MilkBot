import nextcord
from nextcord.ext import commands, tasks
from nextcord.ext.commands import Context

# for log
import asyncio
from datetime import datetime, timedelta
import vk_api

from checkers import check_moderator_permission, check_admin_permissions
from typing import Callable, TypeVar

T = TypeVar("T")


class Mailing(commands.Cog, name="Рассылка"):
    """Рассылка различных сообщений для администраторов"""

    COG_EMOJI = "✉"

    def __init__(self, bot):

        self.bot = bot
        self.horo_send.start()

    @tasks.loop(hours=24)
    async def horo_send(self):

        vk = vk_api.VkApi(token=self.bot.settings["vktoken"]).get_api()

        posts = vk.wall.get(domain="aniscope", count=100)["items"]
        c = 0
        mas = []
        for post in posts:
            text = post["text"]
            if isinstance(text, list):
                textx = ("\n").join(text)
                text = textx
            if (
                text.lower().find("гороскоп") != -1
                and datetime.utcfromtimestamp(post["date"]).date()
                == (datetime.now() - timedelta(days=1)).date()
            ):
                photos = post["attachments"][0]["photo"]["sizes"]
                maxheight = 0
                for photo in photos:
                    maxheight = max(maxheight, photo["height"])
                for photo in photos:
                    if photo["height"] == maxheight:
                        url = photo["url"]
                        if not isinstance(text, list):
                            text = text.split("\n")
                        for txt in text:
                            if txt == "" or txt == " ":
                                text.remove(txt)
                        if [url, text] not in mas:
                            mas.append([url, text])
                            break
                c += 1
            if c == 12:
                break

        await asyncio.sleep(5)
        channels = self.bot.database.get_all_horo()
        embeds = []
        for element in mas:
            emb = nextcord.Embed(description=element[1][2])
            emb.colour = nextcord.Colour.blurple()
            emb.add_field(name=element[1][1], value=f"{element[1][3]}\n{element[1][4]}")
            emb.set_footer(
                text=f'{element[1][0]}\nГороскоп автоматически взят с группы ВК "Аниме гороскопы"'
            )
            emb.set_image(url=element[0])
            embeds.append(emb)

        for channel in channels:
            try:
                channel_object = self.bot.get_channel(channel[0])
                for emb in embeds:
                    await channel_object.send(embed=emb)
                if channel[1] != []:
                    await channel_object.send(
                        " ".join(f"<@&{role}>" for role in channel[1])
                    )
            except:
                continue

    @horo_send.before_loop
    async def before_horo_send(self):
        hour = 0
        minute = 10
        await self.bot.wait_until_ready()
        now = datetime.now()
        future = datetime(now.year, now.month, now.day, hour, minute)
        if now.hour >= hour and now.minute > minute:
            future += timedelta(days=1)
        await asyncio.sleep((future - now).seconds)

    @commands.command(brief="Принудительная отправка гороскопа")
    @commands.check(check_moderator_permission)
    @commands.guild_only()
    async def гороскоп(self, ctx: Context):

        guild_info = self.bot.database.get_guild_info(ctx.guild.id)

        if guild_info:
            today = datetime.now()
            vk = vk_api.VkApi(token=self.bot.settings["vktoken"]).get_api()

            posts = vk.wall.get(domain="aniscope", count=100)["items"]
            c = 0
            mas = []
            for post in posts:
                text = post["text"]
                if isinstance(text, list):
                    textx = ("\n").join(text)
                    text = textx
                if (
                    text.lower().find("гороскоп") != -1
                    and datetime.utcfromtimestamp(post["date"]).date()
                    == (datetime.now() - timedelta(days=1)).date()
                ):
                    photos = post["attachments"][0]["photo"]["sizes"]
                    max_height = 0
                    for photo in photos:
                        max_height = max(max_height, photo["height"])
                    for photo in photos:
                        if photo["height"] == max_height:
                            url = photo["url"]
                            if not isinstance(text, list):
                                text = text.split("\n")
                            for txt in text:
                                if txt == "" or txt == " ":
                                    text.remove(txt)
                            if [url, text] not in mas:
                                mas.append([url, text])
                                break
                    c += 1
                if c == 12:
                    break

            await asyncio.sleep(5)
            embeds = []
            for element in mas:
                emb = nextcord.Embed(description=element[1][2])
                emb.colour = nextcord.Colour.blurple()
                emb.add_field(
                    name=element[1][1], value=f"{element[1][3]}\n\n{element[1][4]}"
                )
                emb.set_footer(
                    text=f'{element[1][0]}\nГороскоп автоматически взят с группы ВК "Аниме гороскопы"'
                )
                emb.set_image(url=element[0])
                embeds.append(emb)

            try:
                for emb in embeds:
                    for channel_id in guild_info.horo_channels:
                        channel = ctx.guild.get_channel(channel_id)
                        await channel.send(embed=emb)
                if guild_info.horo_roles:
                    for channel_id in guild_info.horo_channels:
                        channel = ctx.guild.get_channel(channel_id)
                        await channel.send(
                            " ".join(f"<@&{role}>" for role in guild_info.horo_roles)
                        )
            except Exception as e:
                return self.bot.logger.error(str(e))
        else:
            await ctx.send("Нет настроенного канала для гороскопа")

    @commands.command(brief="Отправка Embed-сообщения из таблицы")
    @commands.check(check_moderator_permission)
    @commands.guild_only()
    async def отправить_embed(self, ctx: Context):

        embeds = self.bot.tables.get_embeds(ctx.guild.id)

        for embed in embeds:
            if embed[0] != "":
                channel = self.bot.get_channel(int(embed[1]))
                if embed[0] != "None":
                    message = await channel.fetch_message(int(embed[0]))
                emb = nextcord.Embed(description=embed[6])

                if embed[2] != "None":
                    emb.title = embed[2]

                if embed[3] == "guild_icon" and ctx.guild.icon:
                    emb.set_thumbnail(url=ctx.guild.icon.url)

                elif embed[3].lower() != "none":
                    emb.set_thumbnail(url=embed[3])

                if embed[4].lower() != "none":
                    emb.set_image(url=embed[4])

                if embed[7] != "":
                    emb.colour = nextcord.Colour.from_rgb(*hex_to_rgb(embed[5][1:]))

                if embed[0] != "None":
                    message = await message.edit(embed=emb)
                else:
                    message = await channel.send(embed=emb)
                self.bot.tables.update_embed(ctx.guild.id, message.id, embed[7])
                await ctx.send(f"{ctx.author.mention}, успешно отправлено!")

    @commands.command(brief="Отправить сообщение в канал", alias=["сказать"])
    @commands.check(check_moderator_permission)
    @commands.guild_only()
    async def отправить(
        self, ctx: Context, канал: nextcord.TextChannel, *, сообщение: str
    ):

        channel = канал
        message = сообщение

        if not isinstance(channel, nextcord.TextChannel):
            return

        try:
            return await channel.send(message)
        except Exception as e:
            return await ctx.send(str(e))

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

    @commands.command(brief="Интерактивное создание Embed блоков", aliases=["embed"])
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


def hex_to_rgb(hex):
    rgb = []
    for i in (0, 2, 4):
        decimal = int(hex[i : i + 2], 16)
        rgb.append(decimal)

    return list(rgb)
