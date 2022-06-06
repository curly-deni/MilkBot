import asyncio
import nextcord
from nextcord.ext import commands, tasks
from nextcord.ext.commands import Context
from nextcord.utils import get

# for multipage embed
from nextcord_paginator import Paginator

from bs4 import BeautifulSoup
import requests
from shikimori_api import Shikimori

import feedparser
from markdownify import markdownify
from lxml import html, etree
from lxml.html.clean import Cleaner
from datetime import datetime, timedelta
from dateutil import parser
import pytz
from time import mktime
from calendar import timegm
import re
import textwrap
from .selectors import *
from typing import Union
from dataclasses import dataclass

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0",
}
shiki_news_rss = "https://shikimori.one/forum/news.rss"


@dataclass
class ShikimoriMember:
    id: int
    name: str
    counter: int


@dataclass
class Anime:
    name: str
    kind: str
    episodes: int
    score: str


@tasks.loop(hours=2)
async def shiki_api():
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

        shiki_api.start()
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
        emb.colour = nextcord.Colour.random()
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

        channels = self.bot.database.get_all_shikimori_releases()
        await asyncio.sleep(5)
        for channel in channels:
            try:
                channel_object = self.bot.get_channel(channel[0])
                await channel_object.send(embed=emb)
                if channel[1]:
                    await channel_object.send(
                        " ".join(f"<@&{role}>" for role in channel[1])
                    )
            except:
                continue

    @send_shikimori_release.before_loop
    async def before_shikimori_release(self):
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
        time = self.bot.database.get_last_news_time()
        if time is None:
            time = datetime(2022, 5, 13, 0, 0, 0)
        last_time = time

        news = []

        for entx in reversed(ent):
            if datetime.fromtimestamp(mktime(entx["published_parsed"])) > time:
                title = entx["title"]

                soup = BeautifulSoup(
                    entx["summary"].replace("&nbsp", " "), "html.parser"
                )

                for tag in soup.find_all("span", class_="name-en"):
                    tag.decompose()

                txt = html.fromstring(f"<body>{str(soup)}</body>")

                cleaner = Cleaner()
                cleaner.remove_tags = ["a"]

                text = markdownify(html.tostring(cleaner.clean_html(txt)))

                publish_time = datetime.fromtimestamp(mktime(entx["published_parsed"]))
                url = entx["link"]

                page = requests.get(url=url, headers=headers)
                soup = BeautifulSoup(page.text, "html.parser")
                a = soup.find_all("a", class_="b-image")
                try:
                    art = a[0]["href"]
                except:
                    art = None

                if art is None:
                    a = soup.find_all("a", class_="video-link")
                    try:
                        art = f'https://img.youtube.com/vi/{a[0]["href"].replace("https://youtu.be/", "")}/hqdefault.jpg'
                    except:
                        art = None

                last_time = max(
                    last_time, datetime.fromtimestamp(mktime(entx["published_parsed"]))
                )

                news.append([title, publish_time, text, art, url])

        news_embeds = []
        self.bot.database.set_last_news_time(last_time)
        for n in news:

            emb: nextcord.Embed = nextcord.Embed(
                title=n[0],
                timestamp=n[1] + timedelta(hours=3),
                colour=nextcord.Colour.random(),
            )

            if len(n[2]) > 6000:
                continue
            elif len(n[2]) > 4096:
                lines = textwrap.wrap(n[2].replace("\n", "_N"), width=4096)
            else:
                lines = [n[2]]
            emb.description = lines[0].replace("_N", "\n")
            lines.remove(lines[0])

            if lines:
                lines = textwrap.wrap(lines[0], width=1024)
                for line in lines:
                    emb.add_field(
                        name="\u200b", value=line.replace("_N", "\n"), inline=False
                    )

            if n[3] is not None:
                try:
                    emb.set_image(url=n[3])
                except:
                    pass

            emb.set_footer(text=f"Новость автоматически взята с портала shikimori.one")
            button = nextcord.ui.View()
            button.add_item(
                nextcord.ui.Button(
                    label="Источник", style=nextcord.ButtonStyle.url, url=n[4]
                )
            )
            news_embeds.append([emb, button])

        channels = self.bot.database.get_all_shikimori_news()
        await asyncio.sleep(10)
        for channel in channels:
            try:
                channel_object = self.bot.get_channel(channel[0])
                for n in news_embeds:
                    try:
                        await channel_object.send(embed=n[0], view=n[1])
                    except:
                        continue
                if channel[1] and news_embeds:
                    await channel_object.send(
                        " ".join(f"<@&{role}>" for role in channel[1])
                    )
            except:
                continue

    @commands.command(brief="Найти персонажа из базы данных Shikimori")
    @commands.guild_only()
    async def персонаж(self, ctx: Context, *, name: str = ""):

        if name == "":
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

            animes = character_info["animes"]
            mangas = character_info["mangas"]

            if animes:
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

        if not emb.fields:
            emb.add_field(
                name="Ошибка 404",
                value="Не найдено героев по вашему запросу",
                inline=False,
            )
            emb.colour = nextcord.Colour.red()
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

            emb.colour = nextcord.Colour.blue()
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
            emb.colour = nextcord.Colour.red()
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
                seyu_str += f"{seyu['name'] if seyu['russian'] is None or seyu['russian'] == '' else seyu['russian']}\n"
            else:
                stop = True

        if animes:
            where = f"Персонаж аниме [{animes[0]['russian']}](https://shikimori.one{animes[0]['url']})\n\n"
        else:
            where = f"Персонаж манги [{mangas[0]['russian']}](https://shikimori.one{mangas[0]['url']})\n\n"

        emb = nextcord.Embed(title=f"{russian_name} | {name}", description=where)
        if ctx.guild.icon:
            emb.set_thumbnail(url=ctx.guild.icon.url)

        if len(description) > 6000:
            lines = []
        elif len(description) > 4096:
            lines = textwrap.wrap(description.replace("\n", "_N"), width=4096)
        else:
            lines = [description]

        if lines:
            emb.description += "**Описание:**\n" + lines[0].replace("_N", "\n")
            lines.remove(lines[0])

        if lines:
            lines = textwrap.wrap(lines[0], width=1024)
            for line in lines:
                emb.add_field(
                    name="\u200b", value=line.replace("_N", "\n"), inline=False
                )

        if image is not None:
            emb.set_image(url=f"https://shikimori.one{image}")

        if animes:
            emb.add_field(name="Аниме", value=anime_str[:-1], inline=False)

            if seyus:
                emb.add_field(name="Сейю", value=seyu_str[:-1], inline=False)

        if mangas:
            emb.add_field(name="Манга", value=manga_str[:-1], inline=False)

        emb.colour = nextcord.Colour.brand_green()
        await message.edit(embed=emb, view=None)

    @commands.command(brief="Найти аниме из базы данных Shikimori")
    @commands.guild_only()
    async def аниме(self, ctx: Context, *, name: str = ""):

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
            emb.colour = nextcord.Colour.red()
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

            emb.colour = nextcord.Colour.blue()
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
            emb.colour = nextcord.Colour.red()
            return await message.edit(embed=emb)

        anime = animes_list[
            reactions_selectors.index(buttons[interaction.data["custom_id"]])
        ]

        name = anime["name"]
        russian_name = anime["russian"]
        score = anime["score"]

        description = re.sub(r"\[(.+)\]", "", anime["description"])

        try:
            image = anime["image"]["original"]
        except:
            image = None

        emb = nextcord.Embed(
            title=f"{name} | {score} ⭐",
            description=f"[{russian_name}](https://shikimori.one{anime['url']})\n\n",
        )
        if image is not None:
            emb.set_thumbnail(url=f"https://shikimori.one{image}")

        if len(description) > 6000:
            lines = []
        elif len(description) > 4096:
            lines = textwrap.wrap(description.replace("\n", "_N"), width=4096)
        else:
            lines = [description]

        if lines:
            emb.description += "**Описание:**\n" + lines[0].replace("_N", "\n")
            lines.remove(lines[0])

        if lines:
            lines = textwrap.wrap(lines[0], width=1024)
            for line in lines:
                emb.add_field(
                    name="\u200b", value=line.replace("_N", "\n"), inline=False
                )

        emb.colour = nextcord.Colour.brand_green()
        await message.edit(embed=emb, view=None)

    @commands.command(
        brief="Топ пользователей сервера по просмотренному на Shikimori",
        aliases=["аниме_топ", "shikimori_top", "anime_top"],
    )
    @commands.guild_only()
    async def шикимори_топ(self, ctx: Context):

        users = self.bot.database.get_shikimori_profiles(ctx.guild.id)
        users_list = []
        for user in users:
            name = get(ctx.guild.members, id=user.id).display_name
            animes = api.users(int(user.shikimori_id)).anime_rates.GET(
                status="completed", limit=5000
            )
            users_list.append(
                ShikimoriMember(id=user.shikimori_id, name=name, counter=len(animes))
            )

        users_list.sort(key=lambda user: user.counter)
        users_list = massive_split(users_list)
        embs = []

        c = 0
        for ulist in users_list:

            emb = nextcord.Embed(title=f"Топ сервера | {ctx.guild.name}")
            emb.colour = nextcord.Colour.green()
            emb.set_thumbnail(url=ctx.guild.icon.url)

            for idx, items in enumerate(ulist):

                emb.add_field(
                    name=f"{c * 10 + idx + 1}. {items.name}",
                    value=f"📺 Просмотрено: {items.counter}",
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
            timeout=0.0,
        )
        try:
            await page.start()
        except nextcord.errors.NotFound:
            pass

    async def shikimori_anime_list(
        self, ctx: Context, пользователь: Union[nextcord.Member, str], type_of_request
    ):
        if isinstance(пользователь, nextcord.Member):
            user = пользователь
        else:
            user = ctx.author

        shikimori_profile = self.bot.database.get_shikimori_profile(
            user.id, ctx.guild.id
        )
        if shikimori_profile is None:
            await ctx.send(f"В базе данных нет записи о ID {user.name}")
            return

        try:
            x = api.users(int(shikimori_profile.shikimori_id)).anime_rates.GET(
                status=type_of_request, limit=5000
            )
        except Exception as e:
            return await ctx.send(f"Произошла ошибка: {e}")

        animes = []

        for y in x:
            animes.append(
                Anime(
                    name=y["anime"]["russian"],
                    kind=y["anime"]["kind"],
                    episodes=y["anime"]["episodes"],
                    score=y["anime"]["score"],
                )
            )

        animes.sort(key=lambda x: x.name)
        animes_len = len(animes)
        animes = massive_split(animes)

        embs = []

        for page, anime in enumerate(animes):

            match type_of_request:
                case "watching":
                    emb = nextcord.Embed(
                        title=f"В процессе просмотра ({animes_len}) | {ctx.author.display_name}"
                    )
                case "planned":
                    emb = nextcord.Embed(
                        title=f"Список запланированного ({animes_len}) | {ctx.author.display_name}"
                    )
                case "completed":
                    emb = nextcord.Embed(
                        title=f"Список просмотренного ({animes_len}) | {ctx.author.display_name}"
                    )

            emb.colour = nextcord.Colour.green()
            emb.set_thumbnail(url=ctx.guild.icon.url)

            for idx, items in enumerate(anime):
                emb.add_field(
                    name=f"{page * 10 + idx + 1}. 📺 {items.name}|{items.score}⭐",
                    value=f"💿 Эпизоды: {items.episodes}|{items.kind.capitalize()}",
                    inline=False,
                )
            if emb.fields:
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
            timeout=0.0,
        )
        try:
            await page.start()
        except nextcord.errors.NotFound:
            pass

    @commands.command(
        brief="Список того, что пользователь смотрит сейчас",
        aliases=["watching", "впроцессе"],
    )
    @commands.guild_only()
    async def в_процессе(
        self, ctx: Context, пользователь: Union[nextcord.Member, str] = ""
    ):
        await self.shikimori_anime_list(ctx, пользователь, "watching")

    @commands.command(
        brief="Список запланированного аниме пользователя", aliases=["planned"]
    )
    @commands.guild_only()
    async def запланировано(
        self, ctx: Context, пользователь: Union[nextcord.Member, str] = ""
    ):
        await self.shikimori_anime_list(ctx, пользователь, "planned")

    @commands.command(
        brief="Список просмотренного пользователя",
        aliases=["просмотренно", "completed", "watched"],
    )
    @commands.guild_only()
    async def просмотрено(
        self, ctx: Context, пользователь: Union[nextcord.Member, str] = ""
    ):
        await self.shikimori_anime_list(ctx, пользователь, "completed")

    @commands.command(
        brief="Добавить свой ID в базу данных. Требуется URL аккаунта Shikimori",
    )
    @commands.guild_only()
    async def шикимори_добавить(self, ctx, url: str = ""):

        if url == "":
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

        emb.colour = nextcord.Colour.blue()

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
            emb.colour = nextcord.Colour.red()
            return await msg.edit(embed=emb)

        if buttons[interaction.data["custom_id"]] == "✅":

            try:
                self.bot.database.add_shikimori_profile(
                    id=ctx.author.id, guild_id=ctx.guild.id, shikimori_id=pid
                )
            except Exception as e:
                await ctx.send(f"Произошла ошибка: {e}")
                return

            emb.title = "Успешно добавлено"
            emb.colour = nextcord.Colour.brand_green()
            await msg.edit(embed=emb, view=None)
        else:
            emb.title = "Отменено"
            emb.colour = nextcord.Colour.red()
            await msg.edit(embed=emb, view=None)


def setup(bot):
    bot.add_cog(ShikimoriStat(bot))
