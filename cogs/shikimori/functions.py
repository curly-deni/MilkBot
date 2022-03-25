# for nextcord
import nextcord
from nextcord.ext import commands
from nextcord.ext import tasks
from nextcord.utils import get

from settings import settings

# for multipage embed
from nextcord_paginator import paginator as Paginator

from bs4 import BeautifulSoup
import requests

from shikimori_api import Shikimori
import json

# with open('shikimori_token.json') as f:
#     token = json.load(f)

session = (
    Shikimori()
)  #'MilkBot', client_id='UJwhP3VvYgOn6pnEn8tRxiH7iiIu5bmhqeVFEUPIavM', client_secret='hEgv-KwTxCmtOqfspKbzhmmbQfjoDBt4WIAGG7PIWjk', token=token)
api = session.get_api()

uri = settings["StatUri"]
connected = False
session = None

import database.shikimori as ShikimoriSQL


@tasks.loop(seconds=60)  # repeat after every 60 seconds
async def reconnect():
    global session
    global connected

    connected = False
    session = ShikimoriSQL.connectToDatabase(uri, session)
    connected = True


def massive_split(mas):
    masx = []
    l10 = len(mas) // 10
    for i in range(l10 + 1):
        masx.append(mas[i * 10 : (i + 1) * 10])
    return masx


class ShikimoriStat(commands.Cog, name="Статистика Shikimori"):
    """Статистика пользователя на Shikimori"""

    COG_EMOJI = "📺"

    def __init__(self, bot):
        self.bot = bot
        reconnect.start()

    @commands.command(brief="Топ пользователей сервера по просмотренному на Шикимори")
    @commands.guild_only()
    async def шикимори_топ(self, ctx):
        global session

        users = ShikimoriSQL.getAllInfo(session, ctx.guild.id)

        userslist = []
        for user in users:
            x = api.users(int(user.sid)).anime_rates.GET(status="completed", limit=5000)
            c = 0
            for y in x:
                c += 1
            userslist.append([user.id, c])

        userslist.sort(key=lambda x: x[1])

        userslist = massive_split(userslist)

        embs = []

        c = 0
        for ulist in userslist:

            emb = nextcord.Embed(title=f"Топ сервера | {ctx.guild.name}")
            emb.color = nextcord.Colour.green()
            emb.set_thumbnail(url=ctx.guild.icon.url)

            for idx, items in enumerate(ulist):

                try:
                    name = get(ctx.guild.members, id=items[0]).display_name
                except:
                    name = "Пользователь покинул сервер"

                emb.add_field(
                    name=f"{c * 10 + idx + 1}. {name}",
                    value=f"📺 Просмотрено: {items[1]}",
                    inline=False,
                )
            c += 1
            embs.append(emb)

        message = await ctx.send(embed=embs[0], delete_after=300)

        page = Paginator(
            message,
            embs,
            ctx.author,
            self.bot,
            footerpage=True,
            footerdatetime=False,
            footerboticon=True,
        )
        try:
            await page.start()
        except nextcord.errors.NotFound:
            pass

    @commands.command(brief="Список того, что пользователь смотрит сейчас")
    @commands.guild_only()
    async def впроцессе(self, ctx, пользователь=None):
        global session

        if пользователь == None:
            user = ctx.author
        else:
            try:
                user = ctx.message.mentions[0]
            except:
                await ctx.send("Отметьте пользователя при вызове команды")
                return

        pid = ShikimoriSQL.getSid(session, ctx.guild.id, user.id)
        if pid == False:
            await ctx.send(f"В базе данных нет записи о ID {user.name}")
            return

        try:
            x = api.users(int(pid)).anime_rates.GET(status="watching", limit=5000)
        except Exception as e:
            await ctx.send(f"Произошла ошибка: {e}")

        animes = []

        for y in x:
            anime = []
            e = y["anime"]
            anime.append(e["russian"])
            anime.append(e["kind"])
            anime.append(e["status"])
            anime.append(e["episodes"])
            anime.append(e["score"])
            animes.append(anime)

        animes.sort(key=lambda x: x[0])
        animes = massive_split(animes)

        embs = []

        c = 0
        for anime in animes:

            emb = nextcord.Embed(
                title=f"В процессе просмотра | {ctx.author.display_name}"
            )
            emb.color = nextcord.Colour.green()
            emb.set_thumbnail(url=ctx.guild.icon.url)

            for idx, items in enumerate(anime):
                emb.add_field(
                    name=f"{c * 10 + idx + 1}. 📺 {items[0]}|{items[4]}⭐",
                    value=f"💿 Эпизоды: {items[3]}|{items[1]}",
                    inline=False,
                )
            c += 1
            embs.append(emb)

        message = await ctx.send(embed=embs[0], delete_after=300)

        page = Paginator(
            message,
            embs,
            ctx.author,
            self.bot,
            footerpage=True,
            footerdatetime=False,
            footerboticon=True,
        )
        try:
            await page.start()
        except nextcord.errors.NotFound:
            pass

    @commands.command(brief="Список запланированного аниме пользователя")
    @commands.guild_only()
    async def запланировано(self, ctx, пользователь=None):
        global session

        if пользователь == None:
            user = ctx.author
        else:
            try:
                user = ctx.message.mentions[0]
            except:
                await ctx.send("Отметьте пользователя при вызове команды")
                return

        pid = ShikimoriSQL.getSid(session, ctx.guild.id, user.id)
        if pid == False:
            await ctx.send(f"В базе данных нет записи о ID {user.name}")
            return

        try:
            x = api.users(int(pid)).anime_rates.GET(status="planned", limit=5000)
        except Exception as e:
            await ctx.send(f"Произошла ошибка: {e}")

        animes = []

        for y in x:
            anime = []
            e = y["anime"]
            anime.append(e["russian"])
            anime.append(e["kind"])
            anime.append(e["status"])
            anime.append(e["episodes"])
            anime.append(e["score"])
            animes.append(anime)

        animes.sort(key=lambda x: x[0])
        animes = massive_split(animes)

        embs = []

        c = 0
        for anime in animes:

            emb = nextcord.Embed(
                title=f"Список запланированного | {ctx.author.display_name}"
            )
            emb.color = nextcord.Colour.green()
            emb.set_thumbnail(url=ctx.guild.icon.url)

            for idx, items in enumerate(anime):
                emb.add_field(
                    name=f"{c * 10 + idx + 1}. 📺 {items[0]}|{items[4]}⭐",
                    value=f"💿 Эпизоды: {items[3]}|{items[1]}",
                    inline=False,
                )
            c += 1
            embs.append(emb)

        message = await ctx.send(embed=embs[0], delete_after=300)

        page = Paginator(
            message,
            embs,
            ctx.author,
            self.bot,
            footerpage=True,
            footerdatetime=False,
            footerboticon=True,
        )
        try:
            await page.start()
        except nextcord.errors.NotFound:
            pass

    @commands.command(brief="Список просмотренного пользователя")
    @commands.guild_only()
    async def просмотрено(self, ctx, пользователь=None):
        global session

        if пользователь == None:
            user = ctx.author
        else:
            try:
                user = ctx.message.mentions[0]
            except:
                await ctx.send("Отметьте пользователя при вызове команды")
                return

        pid = ShikimoriSQL.getSid(session, ctx.guild.id, user.id)
        if pid == False:
            await ctx.send(f"В базе данных нет записи о ID {user.name}")
            return

        try:
            x = api.users(int(pid)).anime_rates.GET(status="completed", limit=5000)
        except Exception as e:
            await ctx.send(f"Произошла ошибка: {e}")

        animes = []

        for y in x:
            anime = []
            e = y["anime"]
            anime.append(e["russian"])
            anime.append(e["kind"])
            anime.append(e["status"])
            anime.append(e["episodes"])
            anime.append(e["score"])
            animes.append(anime)

        animes.sort(key=lambda x: x[0])
        animes = massive_split(animes)

        embs = []

        c = 0
        for anime in animes:

            emb = nextcord.Embed(
                title=f"Список просмотренного | {ctx.author.display_name}"
            )
            emb.color = nextcord.Colour.green()
            emb.set_thumbnail(url=ctx.guild.icon.url)

            for idx, items in enumerate(anime):
                emb.add_field(
                    name=f"{c * 10 + idx + 1}. 📺 {items[0]}|{items[4]}⭐",
                    value=f"💿 Эпизоды: {items[3]}|{items[1]}",
                    inline=False,
                )
            c += 1
            embs.append(emb)

        message = await ctx.send(embed=embs[0], delete_after=300)

        page = Paginator(
            message,
            embs,
            ctx.author,
            self.bot,
            footerpage=True,
            footerdatetime=False,
            footerboticon=True,
        )
        try:
            await page.start()
        except nextcord.errors.NotFound:
            pass

    @commands.command(
        brief="Добавить свой ID в базу данных. Требуется URL аккаунта Shikimori"
    )
    @commands.guild_only()
    async def шикимори_добавить(self, ctx, url=None):
        global session

        if url is None:
            await ctx.send("Укажите URL-профиля Shikimori")
            return

        if not url.startswith("https://shikimori.one/"):
            await ctx.send("Укажите URL-профиля Shikimori")
            return

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
        }
        page = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(page.text, "html.parser")
        a = soup.find("div", class_="profile-head")
        a = str(a).split('">')
        pid = int(a[0].split('data-user-id="')[1])

        try:
            ShikimoriSQL.addInfo(session, ctx.guild.id, ctx.author.id, pid)
        except Exception as e:
            await ctx.send(f"Произошла ошибка: {e}")
            return

        await ctx.send("Успешно добавлено")


def setup(bot):
    bot.add_cog(ShikimoriStat(bot))
