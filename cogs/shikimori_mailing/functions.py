import asyncio
import textwrap
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from time import mktime
from typing import Optional, Union

import feedparser
import nextcord
import requests
from base.base_cog import MilkCog
from bs4 import BeautifulSoup
from dateutil import parser
from lxml import html
from lxml.html.clean import Cleaner
from markdownify import markdownify
from nextcord.ext import commands, tasks
from shikimori_api import Shikimori

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0",
}
shiki_news_rss = "https://shikimori.one/forum/news.rss"
n = "\n"


@dataclass
class AnimeReleaseInfo:
    russian_name: str
    name: str
    image: str
    url: str
    episodes: Union[str, int]
    episodes_aired: Union[str, int]
    score: str


@dataclass
class NewsEntry:
    title: str
    publish_time: datetime
    text: str
    art: Optional[str]
    url: str


@tasks.loop(hours=2)
async def shiki_api():
    global api

    session = Shikimori()
    api = session.get_api()


class ShikimoriMailing(MilkCog, name="Shikimori_Mailing"):
    """Рассылка новостей и релизов с Shikimori"""

    COG_EMOJI: str = "📺"

    def __init__(self, bot):
        self.bot = bot

        shiki_api.start()
        self.send_shikimori_news.start()
        self.send_shikimori_release.start()

    @tasks.loop(hours=24)
    async def send_shikimori_release(self):
        await asyncio.sleep(5)

        page_1: list[dict] = api.topics.updates.GET(page=1, limit=30)
        page_2: list[dict] = api.topics.updates.GET(page=2, limit=30)
        page_3: list[dict] = api.topics.updates.GET(page=3, limit=30)
        page_4: list[dict] = api.topics.updates.GET(page=4, limit=30)

        anime_ids: list = []
        animes: list = []

        now: datetime = datetime.now() - timedelta(days=1)

        for page_element in reversed(page_1 + page_2 + page_3 + page_4):
            if page_element["event"] is not None:
                time: date = parser.parse(page_element["created_at"]).date()
                if time == now.date():
                    anime = page_element["linked"]
                    id: int = int(anime["id"])
                    if id not in anime_ids:
                        anime_info = AnimeReleaseInfo(
                            russian_name=anime["russian"],
                            name=anime["name"],
                            image=f"https://shikimori.one{anime['image']['original']}",
                            url=f"https://shikimori.one{anime['url']}",
                            episodes=anime["episodes"],
                            episodes_aired=anime["episodes_aired"],
                            score=anime["score"],
                        )

                        if float(anime_info.score) != 0.0:
                            animes.append(anime_info)

        emb: nextcord.Embed = nextcord.Embed(
            description=nextcord.utils.format_dt(now, style="D")
        )
        emb.colour = nextcord.Colour.random()
        emb.set_footer(text=f"Новость автоматически взята с портала shikimori.one")
        for anime in animes:
            emb.add_field(
                name=anime.name,
                value=(
                    f"[{anime.russian_name}]({anime.url})\n"
                    + (
                        "**Последний эпизод**\n"
                        if anime.episodes == anime.episodes_aired
                        else ""
                    )
                    + f"💿 **Эпизоды:** {anime.episodes_aired}/{anime.episodes if int(anime.episodes) != 0 else '?'}\n"
                    + f"⭐ **Рейтинг:** {anime.score}/10"
                ),
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

        feed: dict = feedparser.parse(shiki_news_rss)
        entries: list[dict] = feed["entries"]
        time: datetime = self.bot.database.get_last_news_time()
        if time is None:
            time = datetime(2022, 5, 13, 0, 0, 0)
        last_time: datetime = time

        news_list: list[NewsEntry] = []

        for entry in reversed(entries):
            if datetime.fromtimestamp(mktime(entry["published_parsed"])) > time:
                title: str = entry["title"]

                soup: BeautifulSoup = BeautifulSoup(
                    entry["summary"].replace("&nbsp", " "), "html.parser"
                )

                for tag in soup.find_all("span", class_="name-en"):
                    tag.decompose()

                txt: str = html.fromstring(f"<body>{str(soup)}</body>")

                cleaner = Cleaner()
                cleaner.remove_tags = ["a"]

                text: str = markdownify(html.tostring(cleaner.clean_html(txt)))

                publish_time: datetime = datetime.fromtimestamp(
                    mktime(entry["published_parsed"])
                )
                url: str = entry["link"]

                page: requests.Response = requests.get(url=url, headers=headers)
                soup: BeautifulSoup = BeautifulSoup(page.text, "html.parser")
                a_list: list = soup.find_all("a", class_="b-image")
                art = None
                if a_list:
                    if "href" in a_list[0]:
                        art = a_list[0]["href"]

                if art is None:
                    a_list = soup.find_all("a", class_="video-link")
                    if a_list:
                        if "href" in a_list[0]:
                            art = f'https://img.youtube.com/vi/{a_list[0]["href"].replace("https://youtu.be/", "")}/hqdefault.jpg'

                last_time: datetime = max(
                    last_time, datetime.fromtimestamp(mktime(entry["published_parsed"]))
                )
                news_list.append(
                    NewsEntry(
                        title=title,
                        publish_time=publish_time,
                        text=text,
                        art=art,
                        url=url,
                    )
                )

        news_embeds: list[list[nextcord.Embed, nextcord.ui.View]] = []
        self.bot.database.set_last_news_time(last_time)
        for news in news_list:

            emb: nextcord.Embed = nextcord.Embed(
                title=news.title,
                timestamp=news.publish_time + timedelta(hours=3),
                colour=nextcord.Colour.random(),
            )

            if len(news.text) > 6000:
                continue
            elif len(news.text) > 4096:
                lines = textwrap.wrap(news.text.replace("\n", "_N"), width=4096)
            else:
                lines = [news.text]
            emb.description = lines[0].replace("_N", "\n")
            lines.remove(lines[0])

            if lines:
                lines = textwrap.wrap(lines[0], width=1024)
                for line in lines:
                    emb.add_field(
                        name="\u200b", value=line.replace("_N", "\n"), inline=False
                    )

            if news.art is not None:
                try:
                    emb.set_image(url=news.art)
                except:
                    pass

            emb.set_footer(text=f"Новость автоматически взята с портала shikimori.one")
            button = nextcord.ui.View()
            button.add_item(
                nextcord.ui.Button(
                    label="Источник", style=nextcord.ButtonStyle.url, url=news.url
                )
            )
            news_embeds.append([emb, button])

        channels = self.bot.database.get_all_shikimori_news()
        await asyncio.sleep(10)
        for channel in channels:
            try:
                channel_object: nextcord.TextChannel = self.bot.get_channel(channel[0])
                for news in news_embeds:
                    try:
                        await channel_object.send(embed=news[0], view=news[1])
                    except:
                        continue
                if channel[1] and news_embeds:
                    await channel_object.send(
                        " ".join(f"<@&{role}>" for role in channel[1])
                    )
            except:
                continue


def setup(bot):
    bot.add_cog(ShikimoriMailing(bot))
