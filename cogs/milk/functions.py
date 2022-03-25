# This is COG of MilkBot part functions

# for discord
import nextcord
from nextcord.ext import commands
from nextcord.utils import get
from nextcord.ext import tasks
from settings import settings

# for log
import asyncio
from time import time
from datetime import datetime

# for embed
import xml.etree.ElementTree as ET
import database.embed as embed_sheet
from database.serversettings import connectToDatabase, getPrefix, getAdminRole

uri = settings["StatUri"]
gc = None
session = None
Init = False
connected = False

from additional.check_permission import check_permission
from settings import settings

import vk_api

# vk_session = vk_api.VkApi(settings["vklogin"], settings["vkpass"])
# vk_session.auth()
# vk = vk_session.get_api()
#
# time_horo = datetime.strptime("2022-03-24 06:05", "%Y-%m-%d %H:%M")


@tasks.loop(seconds=60)  # repeat after every 60 seconds
async def reconnect():
    global session
    global connected

    connected = False
    session = connectToDatabase(uri, session)
    connected = True


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
        reconnect.start()
        #self.horo_send.start()

    # for future
    # @tasks.loop(time=time_horo.time())
    # async def horo_send(self):
    #     posts = vk.wall.get(domain="neural_horo")["items"]
    #     post = posts[1]
    #     text = post["text"]
    #
    #     channel = self.bot.get_channel(880808624094605362)
    #     args = text.split("\n")
    #     try:
    #         for element in args:
    #             if element != "":
    #                 e = element.split()
    #                 n = e[0][2:].replace(":", "")
    #                 e.pop(0)
    #                 e = " ".join(e)
    #                 com = f"**{n}**\n> {e}"
    #                 await channel.send(com)
    #         await channel.send("<@&881789690586476595>")
    #     except:
    #         pass

    @commands.command(pass_context=True, brief="Конвертация и отправка нейрогороскопа")
    @commands.guild_only()
    async def гороскоп(self, ctx, канал, *, гороскоп):

        mes = канал
        args = гороскоп

        adminroles = getAdminRole(session, ctx.guild.id)
        if check_permission(ctx.author.roles, adminroles):
            try:
                channel = self.bot.get_channel(int(mes))
                args = args.split("\n")
                for element in args:
                    if element != "":
                        e = element.split()
                        n = e[0][1:].replace(":", "")
                        e.pop(0)
                        e = " ".join(e)
                        com = f"**{n}**\n> {e}"
                        await channel.send(com)
            except Exception as mes:
                await ctx.send(str(mes))

    @commands.command(pass_context=True, brief="Отправка Embed-сообщения из таблицы")
    @commands.guild_only()
    async def embed_отправить(self, ctx):
        global gc
        global session
        # [0] MessageUID
        # [1] ChannelUID
        # [2] Title
        # [3] Thumbnail
        # [4] BigImage
        # [5] HEX
        # [6] Field
        # [7] NUM

        adminroles = getAdminRole(session, ctx.guild.id)
        if check_permission(ctx.author.roles, adminroles):
            InitBot()

            g = embed_sheet.getEmbed(gc, session, ctx.guild.id)

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
                            gc, session, ctx.guild.id, message.id, gx[7]
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
                            gc, session, ctx.guild.id, message.id, gx[7]
                        )
                        await ctx.send(f"{ctx.author.mention}, успешно отправлено!")

    @commands.command(pass_context=True, brief="Отправить сообщение в канал")
    @commands.guild_only()
    async def отправить(self, ctx, канал, *, сообщение):

        mes = канал
        args = сообщение

        adminroles = getAdminRole(session, ctx.guild.id)
        if check_permission(ctx.author.roles, adminroles):
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
