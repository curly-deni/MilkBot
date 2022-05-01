# for nextcord
import asyncio

import nextcord
from nextcord.ext import commands
from nextcord.ext import tasks
from nextcord.utils import get

# for multipage embed
from nextcord_paginator import paginator as Paginator

from bs4 import BeautifulSoup
import requests
from shikimori_api import Shikimori

import feedparser
from markdownify import markdownify
from lxml import html
from lxml.html.clean import Cleaner
from datetime import datetime, timedelta
from dateutil import parser
import pytz
from time import mktime
from calendar import timegm
import re
import textwrap

import database.shikimori as ShikimoriSQL
from database.serversettings import getShikimoriNews, getShikimoriRelease
from database.globalsettings import (
    getLastPublishedShikimoriNewsTime,
    setLastPublishedShikimoriNewsTime,
)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
}
shiki_news_rss = "https://shikimori.one/forum/news.rss"

submit = [
    "✅",
    "❌",
]

reactions_selectors = [
    "1️⃣",
    "2️⃣",
    "3️⃣",
    "4️⃣",
    "5️⃣",
    "6️⃣",
    "7️⃣",
    "8️⃣",
    "9️⃣",
    "🔟",
    "🇦",
    "🇧",
    "🇨",
    "🇩",
    "🇪",
    "🇫",
    "🇬",
    "🇭",
    "🇮",
    "🇯",
    "🇰",
    "🇱",
    "🇲",
    "🇳",
    "🇴",
    "🇵",
    "🇶",
    "🇷",
    "🇸",
    "🇹",
    "🇺",
    "🇻",
    "🇼",
    "🇽",
    "🇿",
    "🇾",
]


@tasks.loop(hours=2)
async def shikiapi():
    global api

    session = Shikimori()
    api = session.get_api()


def massive_split(mas):
    masx = []
    l10 = len(mas) // 10
    for i in range(l10 + 1):
        masx.append(mas[i * 10 : (i + 1) * 10])
    return masx


class ShikimoriStat(commands.Cog, name="Shikimori"):
    """Статистика и поиск сведений с Shikimori"""

    COG_EMOJI = "📺"

    def __init__(self, bot):
        self.bot = bot

        shikiapi.start()
        self.send_shikimori_news.start()
        self.send_shikimori_release.start()

    @tasks.loop(hours=24)
    async def send_shikimori_release(self):
        await asyncio.sleep(5)

        x1 = api.topics.updates.GET(page=1, limit=30)
        x2 = api.topics.updates.GET(page=2, limit=30)
        x3 = api.topics.updates.GET(page=3, limit=30)
        x4 = api.topics.updates.GET(page=4, limit=30)

        anime_ids = []
        animes = []

        now = datetime.now(pytz.utc) - timedelta(days=1)

        for xy in reversed(x1 + x2 + x3 + x4):
            if xy["event"] is not None:
                time = parser.parse(xy["created_at"]).date()
                if time == now.date():
                    anime = xy["linked"]
                    id = int(anime["id"])
                    if id not in anime_ids:
                        anime_ids.append(id)
                        russian_name = anime["russian"]
                        name = anime["name"]
                        image = f"https://shikimori.one{anime['image']['original']}"
                        url = f"https://shikimori.one{anime['url']}"
                        episodes = anime["episodes"]
                        episodes_aired = anime["episodes_aired"]
                        score = anime["score"]

                        if float(score) != 0.0:
                            animes.append(
                                [
                                    russian_name,
                                    name,
                                    image,
                                    url,
                                    episodes,
                                    episodes_aired,
                                    score,
                                ]
                            )

        emb = nextcord.Embed(description=f"<t:{timegm(now.timetuple())}:D>")
        emb.color = nextcord.Colour.random()
        emb.set_footer(text=f"Новость автоматически взята с портала shikimori.one")
        for anime in animes:
            if anime[5] == anime[4]:
                emb.add_field(
                    name=f"{anime[1]}",
                    value=f"[{anime[0]}]({anime[3]})\n**Последний эпизод**\n💿 **Эпизоды:** {anime[5]}/{anime[4] if int(anime[4]) != 0 else '?'}\n⭐ **Рейтинг:** {anime[6]}/10",
                    inline=False,
                )
            else:
                emb.add_field(
                    name=f"{anime[1]}",
                    value=f"[{anime[0]}]({anime[3]})\n💿 **Эпизоды:** {anime[5]}/{anime[4] if int(anime[4]) != 0 else '?'}\n⭐ **Рейтинг:** {anime[6]}/10",
                    inline=False,
                )

        channels = getShikimoriRelease(self.bot.databaseSession)
        await asyncio.sleep(10)
        for channelx in channels:
            try:
                channel = self.bot.get_channel(channelx)
                await channel.send(embed=emb)
            except Exception as e:
                print(e)
                pass

    @send_shikimori_release.before_loop
    async def before_shiki_release(self):
        hour = 0
        minute = 10
        await self.bot.wait_until_ready()
        now = datetime.now()
        future = datetime(now.year, now.month, now.day, hour, minute)
        if now.hour >= hour and now.minute > minute:
            future += timedelta(days=1)
        await asyncio.sleep((future - now).seconds)

    @tasks.loop(minutes=5)
    async def send_shikimori_news(self):
        await asyncio.sleep(5)

        feed = feedparser.parse(shiki_news_rss)
        ent = feed["entries"]
        time = getLastPublishedShikimoriNewsTime(self.bot.databaseSession)
        if time is None:
            time = datetime(2022, 4, 1, 0, 0, 0)
        lasttime = time

        news = []

        for entx in reversed(ent):
            if (
                datetime.fromtimestamp(mktime(entx["published_parsed"]))
                - timedelta(minutes=30)
                > time
            ):
                print(entx.keys())
                title = entx["title"]

                txt = html.fromstring(
                    f"<body>{entx['summary'].replace('&nbsp', ' ')}</body>"
                )

                cleaner = Cleaner()
                cleaner.remove_tags = ["a"]

                text = markdownify(html.tostring(cleaner.clean_html(txt)))

                publish_time = f"<t:{timegm(datetime.fromtimestamp(mktime(entx['published_parsed'])).timetuple())}>"
                url = entx["link"]

                page = requests.get(url=url, headers=headers)
                soup = BeautifulSoup(page.text, "html.parser")
                a = soup.find_all("a", class_="b-image")
                try:
                    art = a[0]["href"]
                except:
                    art = None
                    pass

                lasttime = max(
                    lasttime, datetime.fromtimestamp(mktime(entx["published_parsed"]))
                )

                news.append([title, publish_time, text, art, url])

        news_embeds = []
        setLastPublishedShikimoriNewsTime(self.bot.databaseSession, lasttime)
        for n in news:
            emb = nextcord.Embed(description=n[1])
            emb.color = nextcord.Colour.random()

            if len(n[2]) > 1024:
                text_split = n[2].split("\n")
                c = 0
                for line in text_split:
                    if line != "" or line is not None or line != "\n" or line != " ":
                        lines = textwrap.wrap(line, width=1024)
                        g = 0
                        for linex in lines:
                            if g == 0 and c == 0:
                                emb.add_field(name=n[0], value=linex, inline=False)
                            else:
                                emb.add_field(name="\u200b", value=linex, inline=False)
                            g += 1
                        c += 1
                    else:
                        continue

            else:
                emb.add_field(name=n[0], value=n[2], inline=False)

            if n[3] is not None:
                try:
                    emb.set_image(url=n[3])
                except:
                    pass
            emb.set_footer(text=f"Новость автоматически взята с портала shikimori.one")
            news_embeds.append([emb, n[4]])

        channels = getShikimoriNews(self.bot.databaseSession)
        # channels = [959367475324149842]
        await asyncio.sleep(10)
        for channelx in channels:
            try:
                channel = self.bot.get_channel(channelx)
                for n in news_embeds:
                    button = nextcord.ui.View()
                    button.add_item(
                        nextcord.ui.Button(
                            label="Источник", style=nextcord.ButtonStyle.url, url=n[1]
                        )
                    )
                    await channel.send(embed=n[0], view=button)
            except Exception as e:
                print(e)
                pass

    @commands.command(brief="Найти персонажа из базы данных Shikimori")
    @commands.guild_only()
    async def персонаж(self, ctx, *, name=None):

        if name is None:
            m1 = await ctx.send("Укажите имя")
            try:
                msg = await self.bot.wait_for(
                    "message",
                    timeout=60.0,
                    check=lambda m: m.channel == ctx.channel
                    and m.author.id == ctx.author.id,
                )
                name = msg.content
            except asyncio.TimeoutError:
                await m1.delete()
                return

        characters = api.characters.search.GET(search=name)
        characters_list = []
        characters_short_descriptions = []
        emb = nextcord.Embed(title=f"Поиск героев по имени {name}")
        for idx, item in enumerate(characters):
            character = item
            try:
                character_info = api.characters(character["id"]).GET()
            except:
                continue
            characters_list.append(character_info)

            name = character_info["name"]
            russian_name = character_info["russian"]

            # image = character_info['image']['original']

            animes = character_info["animes"]
            mangas = character_info["mangas"]

            if animes != []:
                where = f"Персонаж аниме [{animes[0]['russian']}](https://shikimori.one{animes[0]['url']})"
            else:
                where = f"Персонаж манги [{mangas[0]['russian']}](https://shikimori.one{mangas[0]['url']})"

            characters_short_descriptions.append([f"{russian_name}|{name}", where])

        for idx, item in enumerate(characters_short_descriptions):
            emb.add_field(
                name=f"{reactions_selectors[idx]}. {item[0]}",
                value=item[1],
                inline=False,
            )

        if len(emb.fields) == 0:
            emb.add_field(
                name="Ошибка 404",
                value="Не найдено героев по вашему запросу",
                inline=False,
            )
            emb.color = nextcord.Colour.red()
            return await ctx.send(embed=emb)

        else:
            view = nextcord.ui.View()
            buttons = {}
            for i in range(len(characters_short_descriptions)):
                try:
                    button = nextcord.ui.Button(
                        style=nextcord.ButtonStyle.secondary,
                        emoji=reactions_selectors[i],
                    )
                    buttons[button.custom_id] = reactions_selectors[i]
                    view.add_item(button)
                except:
                    continue

            emb.color = nextcord.Colour.blue()
            message = await ctx.send(embed=emb, view=view)

        try:
            interaction = await self.bot.wait_for(
                "interaction",
                timeout=60.0,
                check=lambda m: m.user.id == ctx.author.id
                and m.message.id == message.id
                # and str(m.emoji) in submit,
            )
        except asyncio.TimeoutError:
            emb.set_footer(text="Время вышло")
            emb.color = nextcord.Colour.red()
            return await message.edit(embed=emb)

        character = characters_list[
            reactions_selectors.index(buttons[interaction.data["custom_id"]])
        ]

        name = character["name"]
        russian_name = character["russian"]

        try:
            txt = etree.fromstring(f"<body>{character['description_html']}</body>")
            etree.strip_tags(txt, "a")
            description = markdownify(etree.tostring(txt))
        except:
            # description = character['description']
            description = re.sub(r"\[(.+)\]", "", character["description"])
            pass

        description_array = []

        if len(description) > 1024:
            description = description.split("\n")
            c = 0
            for line in description:
                if line != "" or line is not None or line != "\n" or line != " ":
                    lines = textwrap.wrap(line, width=1024)
                    g = 0
                    for linex in lines:
                        if g == 0 and c == 0:
                            description_array.append(["Описание", linex])
                        else:
                            description_array.append(["\u200b", linex])
                        g += 1
                    c += 1
                else:
                    continue
        else:
            description_array.append(["Описание", description])

        animes = character["animes"]
        mangas = character["mangas"]
        seyus = character["seyu"]

        try:
            image = character["image"]["original"]
        except:
            image = None

        anime_str = ""
        stop = False
        for anime in animes:
            if not stop and len(anime_str + anime["russian"]) <= 1024:
                anime_str += f"{anime['russian']}\n"
            else:
                stop = True

        manga_str = ""
        stop = False
        for manga in mangas:
            if not stop and len(manga_str + manga["russian"]) <= 1024:
                manga_str += f"{manga['russian']}\n"
            else:
                stop = True

        seyu_str = ""
        stop = False
        for seyu in seyus:
            if not stop and len(seyu_str + seyu["name"]) <= 1024:
                seyu_str += f"{seyu['name'] if seyu['russian'] == None or seyu['russian'] == '' else seyu['russian']}\n"
            else:
                stop = True

        if animes != []:
            where = f"Персонаж аниме [{animes[0]['russian']}](https://shikimori.one{animes[0]['url']})"
        else:
            where = f"Персонаж манги [{mangas[0]['russian']}](https://shikimori.one{mangas[0]['url']})"

        emb = nextcord.Embed(title=f"{russian_name}|{name}", description=where)
        if image is not None:
            emb.set_thumbnail(url=f"https://shikimori.one{image}")

        # desc
        for desc_line in description_array:
            emb.add_field(name=desc_line[0], value=desc_line[1], inline=False)

        if animes != []:
            emb.add_field(name="Аниме", value=anime_str[:-1], inline=False)

            if seyus != []:
                emb.add_field(name="Сейю", value=seyu_str[:-1], inline=False)

        if mangas != []:
            emb.add_field(name="Манга", value=manga_str[:-1], inline=False)

        emb.color = nextcord.Colour.brand_green()
        await message.edit(embed=emb, view=None)

    @commands.command(brief="Найти аниме из базы данных Shikimori")
    @commands.guild_only()
    async def аниме(self, ctx, *, name=None):

        if name is None:
            m1 = await ctx.send("Укажите название")
            try:
                msg = await self.bot.wait_for(
                    "message",
                    timeout=60.0,
                    check=lambda m: m.channel == ctx.channel
                    and m.author.id == ctx.author.id,
                )
                name = msg.content
            except asyncio.TimeoutError:
                await m1.delete()
                return

        animes = api.animes.GET(search=name, limit=20)
        animes_list = []
        animes_short_descriptions = []
        emb = nextcord.Embed(title=f"Поиск аниме по названию {name}")
        for idx, item in enumerate(animes):
            anime = item
            try:
                anime_info = api.animes(anime["id"]).GET()
            except:
                continue
            animes_list.append(anime_info)

            name = anime_info["name"]
            russian_name = anime_info["russian"]
            score = anime_info["score"]

            # image = anime_info['image']['original']

            animes_short_descriptions.append(
                [
                    f"{name}|{score}⭐",
                    f'[{russian_name}](https://shikimori.one{anime_info["url"]})',
                ]
            )

        for idx, item in enumerate(animes_short_descriptions):
            emb.add_field(
                name=f"{reactions_selectors[idx]}. {item[0]}",
                value=item[1],
                inline=False,
            )

        if len(emb.fields) == 0:
            emb.add_field(
                name="Ошибка 404",
                value="Не найдено аниме по вашему запросу",
                inline=False,
            )
            emb.color = nextcord.Colour.red()
            return await ctx.send(embed=emb)

        else:
            view = nextcord.ui.View()
            buttons = {}
            for i in range(len(animes_short_descriptions)):
                try:
                    button = nextcord.ui.Button(
                        style=nextcord.ButtonStyle.secondary,
                        emoji=reactions_selectors[i],
                    )
                    buttons[button.custom_id] = reactions_selectors[i]
                    view.add_item(button)
                except:
                    continue

            emb.color = nextcord.Colour.blue()
            message = await ctx.send(embed=emb, view=view)

        try:
            interaction = await self.bot.wait_for(
                "interaction",
                timeout=60.0,
                check=lambda m: m.user.id == ctx.author.id
                and m.message.id == message.id
                # and str(m.emoji) in submit,
            )
        except asyncio.TimeoutError:
            emb.set_footer(text="Время вышло")
            emb.color = nextcord.Colour.red()
            return await message.edit(embed=emb)

        anime = animes_list[
            reactions_selectors.index(buttons[interaction.data["custom_id"]])
        ]

        name = anime["name"]
        russian_name = anime["russian"]
        score = anime["score"]

        # try:
        #     txt = etree.fromstring(f"<body>{anime['description_html']}</body>")
        #     etree.strip_tags(txt, 'a')
        #     description = markdownify(etree.tostring(txt))
        # except:
        #     # description = anime['description']
        description = re.sub(r"\[(.+)\]", "", anime["description"])
        #     pass

        description_array = []

        if len(description) > 1024:
            description = description.split("\n")
            c = 0
            for line in description:
                if line != "" or line is not None or line != "\n" or line != " ":
                    lines = textwrap.wrap(line, width=1024)
                    g = 0
                    for linex in lines:
                        if g == 0 and c == 0:
                            description_array.append(["Описание", linex])
                        else:
                            description_array.append(["\u200b", linex])
                        g += 1
                    c += 1
                else:
                    continue
        else:
            description_array.append(["Описание", description])

        try:
            image = anime["image"]["original"]
        except:
            image = None

        emb = nextcord.Embed(
            title=f"{name}|{score}⭐",
            description=f"[{russian_name}](https://shikimori.one{anime['url']})",
        )
        if image is not None:
            emb.set_thumbnail(url=f"https://shikimori.one{image}")

        for desc_line in description_array:
            emb.add_field(name=desc_line[0], value=desc_line[1], inline=False)

        emb.color = nextcord.Colour.brand_green()
        await message.edit(embed=emb, view=None)

    @commands.command(brief="Топ пользователей сервера по просмотренному на Шикимори")
    @commands.guild_only()
    async def шикимори_топ(self, ctx):

        users = ShikimoriSQL.getAllInfo(self.bot.databaseSession, ctx.guild.id)

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

        if пользователь is None:
            user = ctx.author
        else:
            try:
                user = ctx.message.mentions[0]
            except:
                await ctx.send("Отметьте пользователя при вызове команды")
                return

        pid = ShikimoriSQL.getSid(self.bot.databaseSession, ctx.guild.id, user.id)
        if pid is None:
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

        if пользователь is None:
            user = ctx.author
        else:
            try:
                user = ctx.message.mentions[0]
            except:
                await ctx.send("Отметьте пользователя при вызове команды")
                return

        pid = ShikimoriSQL.getSid(self.bot.databaseSession, ctx.guild.id, user.id)
        if pid is None:
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

        if пользователь is None:
            user = ctx.author
        else:
            try:
                user = ctx.message.mentions[0]
            except:
                await ctx.send("Отметьте пользователя при вызове команды")
                return

        pid = ShikimoriSQL.getSid(self.bot.databaseSession, ctx.guild.id, user.id)
        if pid is None:
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

        if url is None:
            await ctx.send("Укажите URL-профиля Shikimori")
            return

        if not url.startswith("https://shikimori.one/"):
            await ctx.send("Укажите URL-профиля Shikimori")
            return

        page = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(page.text, "html.parser")
        a = soup.find("div", class_="profile-head")
        a = str(a).split('">')
        pid = int(a[0].split('data-user-id="')[1])

        user = api.users(pid).GET()

        emb = nextcord.Embed(
            title=f"{ctx.author.display_name}, проверьте введённые данные"
        )

        emb.add_field(name="Никнейм", value=user["nickname"], inline=False)

        emb.set_thumbnail(url=user["avatar"])

        emb.color = nextcord.Colour.blue()

        view = nextcord.ui.View()
        buttons = {}
        for reaction in submit:
            button = nextcord.ui.Button(
                style=nextcord.ButtonStyle.secondary, emoji=reaction
            )
            buttons[button.custom_id] = reaction
            view.add_item(button)

        msg = await ctx.send(embed=emb, view=view)

        try:
            interaction = await self.bot.wait_for(
                "interaction",
                timeout=60.0,
                check=lambda m: m.user.id == ctx.author.id and m.message.id == msg.id
                # and str(m.emoji) in submit,
            )
        except asyncio.TimeoutError:
            emb.set_footer(text="Время вышло")
            emb.color = nextcord.Colour.red()
            return await msg.edit(embed=emb)

        if buttons[interaction.data["custom_id"]] == "✅":

            try:
                ShikimoriSQL.addInfo(
                    self.bot.databaseSession, ctx.guild.id, ctx.author.id, pid
                )
            except Exception as e:
                await ctx.send(f"Произошла ошибка: {e}")
                return

            emb.title = "Успешно добавлено"
            emb.color = nextcord.Colour.brand_green()
            await msg.edit(embed=emb, view=None)
        else:
            emb.title = "Отменено"
            emb.color = nextcord.Colour.red()
            await msg.edit(embed=emb, view=None)


def setup(bot):
    bot.add_cog(ShikimoriStat(bot))
