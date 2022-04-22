# This is COG of MilkBot part functions

# for discord
import nextcord
from nextcord.ext import commands, tasks
from nextcord.utils import get
from settings import settings

# for log
import asyncio
from time import time
from datetime import datetime, timedelta

from additional.check_permission import check_admin_permissions

from settings import settings

import vk_api
from calendar import timegm

import locale
import pymorphy2

# for embed
import xml.etree.ElementTree as ET
import database.embed as embed_sheet
from database.serversettings import (
    getPrefix,
    getAdminRole,
    getHoro,
    getInfo,
)

locale.setlocale(locale.LC_ALL, "")
morph = pymorphy2.MorphAnalyzer()

uri = settings["StatUri"]
gc = None

Init = False


def InitBot():
    global gc
    global Init

    if not Init:
        gc = embed_sheet.gcAuthorize()
        print(f"{datetime.now()}|Successful init.")
        Init = True


class Milk(commands.Cog, name="Рассылка"):
    """Рассылка различных сообщений для администраторов"""

    COG_EMOJI = "✉"

    def __init__(self, bot):

        self.bot = bot

        self.horo_send.start()

    @tasks.loop(hours=24)
    async def horo_send(self):


        today = datetime.now()
        d = (
            str(today.day)
            + " "
            + morph.parse(datetime.strftime(today, "%B"))[0].inflect({"gent"}).word
        )

        vk = vk_api.VkApi(token=settings['vktoken']).get_api()

        posts = vk.wall.get(domain="aniscope", count=100)["items"]
        c = 0
        mas = []
        for post in posts:
            text = post["text"]
            if isinstance(text, list):
                textx = ("\n").join(text)
                text = textx
            if text.find(d) != -1:
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
                c += 1
            if c == 12:
                break

        await asyncio.sleep(10)
        channels = getHoro(self.bot.databaseSession)
        embeds = []
        for element in mas:
            emb = nextcord.Embed(description=element[1][2])
            emb.color = nextcord.Colour.blurple()
            emb.add_field(name=element[1][1], value=f"{element[1][3]}\n{element[1][4]}")
            emb.set_footer(
                text=f'{element[1][0]}\nГороскоп автоматически взят с группы ВК "Аниме гороскопы"'
            )
            emb.set_image(url=element[0])
            embeds.append(emb)

        for channelx in channels:
            try:
                channel = self.bot.get_channel(channelx[0])
                for emb in embeds:
                    await channel.send(embed=emb)
                if channelx[1]:
                    await channel.send(f"<@&{channelx[1]}>")
            except Exception as e:
                pass

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

    @commands.command(pass_context=True, brief="Принудительная отправка гороскопа")
    @commands.check(check_admin_permissions)
    @commands.guild_only()
    async def гороскоп(self, ctx):

        info = getInfo(self.bot.databaseSession, ctx.guild.id)

        if info.horo:
            today = datetime.now()
            d = (
                str(today.day)
                + " "
                + morph.parse(datetime.strftime(today, "%B"))[0].inflect({"gent"}).word
            )

            vk = vk_api.VkApi(token=settings['vktoken']).get_api()

            posts = vk.wall.get(domain="aniscope", count=100)["items"]
            c = 0
            mas = []
            for post in posts:
                text = post["text"]
                if isinstance(text, list):
                    textx = ("\n").join(text)
                    text = textx
                if text.find(d) != -1:
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
                    c += 1
                if c == 12:
                    break

            await asyncio.sleep(10)
            embeds = []
            for element in mas:
                emb = nextcord.Embed(description=element[1][2])
                emb.color = nextcord.Colour.blurple()
                emb.add_field(
                    name=element[1][1], value=f"{element[1][3]}\n{element[1][4]}"
                )
                emb.set_footer(
                    text=f'{element[1][0]}\nГороскоп автоматически взят с группы ВК "Аниме гороскопы"'
                )
                emb.set_image(url=element[0])
                embeds.append(emb)

            try:
                for emb in embeds:
                    await self.bot.get_channel(info.horochannel).send(embed=emb)
                if info.hororole:
                    await self.bot.get_channel(info.horochannel).send(
                        f"<@&{info.hororole}>"
                    )
            except Exception as e:
                await ctx.send(str(e))
                pass

        else:
            await ctx.send("Нет настроенного канала для гороскопа")

    @commands.command(pass_context=True, brief="Отправка Embed-сообщения из таблицы")
    @commands.check(check_admin_permissions)
    @commands.guild_only()
    async def embed_отправить(self, ctx):
        global gc

        # [0] MessageUID
        # [1] ChannelUID
        # [2] Title
        # [3] Thumbnail
        # [4] BigImage
        # [5] HEX
        # [6] Field
        # [7] NUM

        InitBot()

        g = embed_sheet.getEmbed(gc, self.bot.databaseSession, ctx.guild.id)

        for gx in g:
            if gx[0] != "":
                if gx[0] == "None":
                    channel = self.bot.get_channel(int(gx[1]))
                    emb = nextcord.Embed(title=gx[2])

                    if gx[3] == "guild.icon":
                        emb.set_thumbnail(url=ctx.guild.icon.url)

                    elif gx[3].lower() != "none":
                        emb.set_thumbnail(url=gx[3])

                    if gx[4].lower() != "none":
                        emb.set_image(url=gx[4])

                    if gx[7] != "":
                        emb.color = nextcord.Colour.from_rgb(*hex_to_rgb(gx[5][1:]))

                    z = f"<data>\n{gx[6]}\n</data>"

                    root = ET.fromstring(z)

                    for fiel in root.findall("field"):
                        emb.add_field(
                            name=fiel.find("title").text,
                            value=fiel.find("text").text.replace("\\n", "\n"),
                            inline=fiel.find("inline").text,
                        )

                    message = await channel.send(embed=emb)
                    embed_sheet.updateEmbed(
                        gc,
                        self.bot.databaseSession,
                        ctx.guild.id,
                        message.id,
                        gx[7],
                    )
                    await ctx.send(f"{ctx.author.mention}, успешно отправлено!")
                else:
                    channel = self.bot.get_channel(int(gx[1]))
                    message = await channel.fetch_message(int(gx[0]))
                    emb = nextcord.Embed(title=gx[2])

                    if gx[3] == "guild.icon":
                        emb.set_thumbnail(url=ctx.guild.icon.url)

                    elif gx[3].lower() != "none":
                        emb.set_thumbnail(url=gx[3])

                    if gx[4].lower() != "none":
                        emb.set_image(url=gx[4])

                    if gx[7] != "":
                        emb.color = nextcord.Colour.from_rgb(*hex_to_rgb(gx[5][1:]))

                    root = ET.fromstring(f"<data>\n{gx[6]}\n</data>")

                    for fiel in root.findall("field"):
                        emb.add_field(
                            name=fiel.find("title").text,
                            value=fiel.find("text").text.replace("\\n", "\n"),
                            inline=fiel.find("inline").text,
                        )

                    message = await message.edit(embed=emb)
                    embed_sheet.updateEmbed(
                        gc,
                        self.bot.databaseSession,
                        ctx.guild.id,
                        message.id,
                        gx[7],
                    )
                    await ctx.send(f"{ctx.author.mention}, успешно отправлено!")

    @commands.command(pass_context=True, brief="Отправить сообщение в канал")
    @commands.check(check_admin_permissions)
    @commands.guild_only()
    async def отправить(self, ctx, канал, *, сообщение):

        mes = канал
        args = сообщение

        try:
            channel = self.bot.get_channel(int(mes))
            await channel.send(args)
            return
        except Exception as mes:
            await ctx.send(str(mes))
            return


def setup(bot):
    bot.add_cog(Milk(bot))


def hex_to_rgb(hex):
    rgb = []
    for i in (0, 2, 4):
        decimal = int(hex[i : i + 2], 16)
        rgb.append(decimal)

    return list(rgb)
