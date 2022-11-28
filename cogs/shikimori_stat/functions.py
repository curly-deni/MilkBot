import asyncio
import re
import textwrap
from dataclasses import dataclass
from typing import Optional

import nextcord
import requests
from base.base_cog import MilkCog
from bs4 import BeautifulSoup
from lxml import etree
from markdownify import markdownify
from modules.paginator import Paginator
from modules.utils import list_split
from nextcord.ext import tasks
from nextcord.utils import get
from shikimori_api import Shikimori

from .selectors import *

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0",
}
shiki_news_rss = "https://shikimori.one/forum/news.rss"
n = "\n"


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


class ShikimoriStat(MilkCog, name="Shikimori"):
    """Статистика и поиск сведений с Shikimori"""

    COG_EMOJI: str = "📺"

    def __init__(self, bot):
        self.bot = bot

        shiki_api.start()

    @MilkCog.slash_command(description="Найти персонажа аниме (манги) на Shikimori")
    async def character(
        self,
        interaction: nextcord.Interaction,
        name: Optional[str] = nextcord.SlashOption(
            name="имя", description="имя разыскиваемого персонажа", required=True
        ),
    ):
        await interaction.response.defer()

        characters: list[dict] = api.characters.search.GET(search=name)
        characters_list: list[dict] = []
        characters_short_descriptions: list = []
        emb: nextcord.Embed = nextcord.Embed(title=f"Поиск героев по имени {name}")
        for idx, character in enumerate(characters):
            try:
                character_info: dict = api.characters(character["id"]).GET()
            except:
                continue
            characters_list.append(character_info)

            name: str = character_info["name"]
            russian_name: str = character_info["russian"]

            animes: list[dict] = character_info["animes"]
            mangas: list[dict] = character_info["mangas"]

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
            return await interaction.followup.send(embed=emb)

        else:
            view: nextcord.ui.View = nextcord.ui.View()
            buttons: dict = {}
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
            message: nextcord.Message = await interaction.followup.send(
                embed=emb, view=view
            )

        try:
            interaction: nextcord.Interaction = await self.bot.wait_for(
                "interaction",
                timeout=60.0,
                check=lambda m: m.user.id == interaction.user.id
                and m.message.id == message.id
                # and str(m.emoji) in submit,
            )
        except asyncio.TimeoutError:
            emb.set_footer(text="Время вышло")
            emb.colour = nextcord.Colour.red()
            return await message.edit(embed=emb)

        character: dict = characters_list[
            reactions_selectors.index(buttons[interaction.data["custom_id"]])
        ]

        name: str = character["name"]
        russian_name: str = character["russian"]

        try:
            txt: etree.ElementTree = etree.fromstring(
                f"<body>{character['description_html']}</body>"
            )
            etree.strip_tags(txt, "a")
            description: str = markdownify(etree.tostring(txt))
        except:
            description: str = re.sub(r"\[(.+)\]", "", character["description"])

        animes: list[dict] = character["animes"]
        mangas: list[dict] = character["mangas"]
        seyus: list[dict] = character["seyu"]

        image: Optional[str] = None
        if "image" in character:
            if "original" in character["image"]:
                image: str = character["image"]["original"]

        anime_str: str = ""
        for anime in animes:
            if len(anime_str + anime["russian"]) <= 1024:
                anime_str += f"{anime['russian']}\n"
            else:
                break

        manga_str: str = ""
        for manga in mangas:
            if len(manga_str + manga["russian"]) <= 1024:
                manga_str += f"{manga['russian']}\n"
            else:
                break

        seyu_str = ""
        for seyu in seyus:
            if len(seyu_str + seyu["name"]) <= 1024:
                seyu_str += f"{seyu['name'] if seyu['russian'] is None or seyu['russian'] == '' else seyu['russian']}\n"
            else:
                break

        if animes:
            where = f"Персонаж аниме [{animes[0]['russian']}](https://shikimori.one{animes[0]['url']})\n\n"
        else:
            where = f"Персонаж манги [{mangas[0]['russian']}](https://shikimori.one{mangas[0]['url']})\n\n"

        emb: nextcord.Embed = nextcord.Embed(
            title=f"{russian_name} | {name}", description=where
        )
        if interaction.guild.icon:
            emb.set_thumbnail(url=interaction.guild.icon.url)

        if len(description) > 6000:
            lines: list = []
        elif len(description) > 4096:
            lines: list[str] = textwrap.wrap(
                description.replace("\n", "_N"), width=4096
            )
        else:
            lines: list[str] = [description]

        if lines:
            emb.description += "**Описание:**\n" + lines[0].replace("_N", "\n")
            lines.remove(lines[0])

        if lines:
            lines: list[str] = textwrap.wrap(lines[0], width=1024)
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

    @MilkCog.slash_command(description="Найти аниме на Shikimori")
    async def anime(
        self,
        interaction: nextcord.Interaction,
        name: Optional[str] = nextcord.SlashOption(
            name="название", description="название разыскиваемого аниме", required=True
        ),
    ):
        await interaction.response.defer()

        animes: list[dict] = api.animes.GET(search=name, limit=20)
        animes_list: list[dict] = []
        animes_short_descriptions: list[list[str]] = []
        emb = nextcord.Embed(title=f"Поиск аниме по названию {name}")
        for idx, anime in enumerate(animes):
            try:
                anime_info: dict = api.animes(anime["id"]).GET()
            except:
                continue
            animes_list.append(anime_info)

            name: str = anime_info["name"]
            russian_name: str = anime_info["russian"]
            score: str = anime_info["score"]

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

        if not emb.fields:
            emb.add_field(
                name="Ошибка 404",
                value="Не найдено аниме по вашему запросу",
                inline=False,
            )
            emb.colour = nextcord.Colour.red()
            return await interaction.followup.send(embed=emb)

        else:
            view: nextcord.ui.View = nextcord.ui.View()
            buttons: dict = {}
            for i in range(len(animes_short_descriptions)):
                try:
                    button: nextcord.ui.Button = nextcord.ui.Button(
                        style=nextcord.ButtonStyle.secondary,
                        emoji=reactions_selectors[i],
                    )
                    buttons[button.custom_id] = reactions_selectors[i]
                    view.add_item(button)
                except:
                    continue

            emb.colour = nextcord.Colour.blue()
            message: nextcord.Message = await interaction.followup.send(
                embed=emb, view=view
            )

        try:
            interaction: nextcord.Interaction = await self.bot.wait_for(
                "interaction",
                timeout=60.0,
                check=lambda m: m.user.id == interaction.user.id
                and m.message.id == message.id
                # and str(m.emoji) in submit,
            )
        except asyncio.TimeoutError:
            emb.set_footer(text="Время вышло")
            emb.colour = nextcord.Colour.red()
            return await message.edit(embed=emb)

        anime: dict = animes_list[
            reactions_selectors.index(buttons[interaction.data["custom_id"]])
        ]

        name: str = anime["name"]
        russian_name: str = anime["russian"]
        score: str = anime["score"]

        description: str = re.sub(r"\[(.+)\]", "", anime["description"])

        image: Optional[str] = None
        if "image" in anime:
            if "original" in anime["image"]:
                image: str = anime["image"]["original"]

        emb: nextcord.Embed = nextcord.Embed(
            title=f"{name} | {score} ⭐",
            description=f"[{russian_name}](https://shikimori.one{anime['url']})\n\n",
        )
        if image is not None:
            emb.set_image(url=f"https://shikimori.one{image}")

        if len(description) > 6000:
            lines: list = []
        elif len(description) > 4096:
            lines: list[str] = textwrap.wrap(
                description.replace("\n", "_N"), width=4096
            )
        else:
            lines: list[str] = [description]

        if lines:
            emb.description += "**Описание:**\n" + lines[0].replace("_N", "\n")
            lines.remove(lines[0])

        if lines:
            lines: list[str] = textwrap.wrap(lines[0], width=1024)
            for line in lines:
                emb.add_field(
                    name="\u200b", value=line.replace("_N", "\n"), inline=False
                )

        emb.colour = nextcord.Colour.brand_green()
        await message.edit(embed=emb, view=None)

    @MilkCog.slash_command(
        description="Топ пользователей по просмотренному аниме на Shikimori",
    )
    async def shikimori_leaders(self, interaction: nextcord.Interaction):

        await interaction.response.defer(ephemeral=True)

        users: list = self.bot.database.get_shikimori_profiles(interaction.guild.id)
        users_list: list[ShikimoriMember] = []
        for user in users:
            name: str = get(interaction.guild.members, id=user.id).display_name
            animes: list[dict] = api.users(int(user.shikimori_id)).anime_rates.GET(
                status="completed", limit=5000
            )
            users_list.append(
                ShikimoriMember(id=user.shikimori_id, name=name, counter=len(animes))
            )

        users_list.sort(key=lambda user: user.counter)
        users_list: list[list[ShikimoriMember]] = list_split(users_list)
        embs: list[nextcord.Embed] = []

        for page, user_list in enumerate(users_list):

            emb: nextcord.Embed = nextcord.Embed(
                title=f"Топ сервера | {interaction.guild.name}"
            )
            emb.colour = nextcord.Colour.green()
            emb.set_thumbnail(url=interaction.guild.icon.url)

            for num, items in enumerate(user_list):
                emb.add_field(
                    name=f"{page * 10 + num + 1}. {items.name}",
                    value=f"📺 Просмотрено: {items.counter}",
                    inline=False,
                )
            if emb.fields:
                embs.append(emb)

        message: nextcord.Message = await interaction.followup.send(
            embed=embs[0], delete_after=300
        )

        paginator: Paginator = Paginator(
            message,
            embs,
            interaction.user,
            self.bot,
            footerpage=True,
            footerdatetime=False,
            footerboticon=True,
            timeout=180.0,
        )
        try:
            await paginator.start()
        except nextcord.errors.NotFound:
            pass

    @MilkCog.slash_command(
        description="Проосмотр списка аниме пользователя",
    )
    async def anime_list(
        self,
        interaction: nextcord.Interaction,
        type: str = nextcord.SlashOption(
            name="тип",
            description="тип списка",
            choices={
                "просмотрено": "completed",
                "в процессе": "watching",
                "запланировано": "planned",
            },
            required=True,
        ),
        user: Optional[nextcord.Member] = nextcord.SlashOption(
            name="пользователь",
            description="участник сервера",
            required=False,
        ),
    ):

        await interaction.response.defer(ephemeral=True)

        if not isinstance(user, nextcord.Member):
            user = interaction.user

        shikimori_profile = self.bot.database.get_shikimori_profile(
            user.id, interaction.guild.id
        )
        if shikimori_profile is None:
            return await interaction.followup.send(
                f"В базе данных нет записи о ID {user.name}"
            )

        try:
            requested_list: list[dict] = api.users(
                int(shikimori_profile.shikimori_id)
            ).anime_rates.GET(status=type, limit=5000)
        except Exception as e:
            return await interaction.followup.send(f"Произошла ошибка: {e}")

        animes: list[Anime] = []

        for anime in requested_list:
            animes.append(
                Anime(
                    name=anime["anime"]["russian"],
                    kind=anime["anime"]["kind"],
                    episodes=anime["anime"]["episodes"],
                    score=anime["anime"]["score"],
                )
            )

        animes.sort(key=lambda x: x.name)
        animes_len: int = len(animes)
        animes: list[list[Anime]] = list_split(animes)

        embs: list[nextcord.Embed] = []

        for page, anime in enumerate(animes):

            match type:
                case "watching":
                    emb: nextcord.Embed = nextcord.Embed(
                        title=f"В процессе просмотра ({animes_len}) | {user.display_name}"
                    )
                case "planned":
                    emb: nextcord.Embed = nextcord.Embed(
                        title=f"Список запланированного ({animes_len}) | {user.display_name}"
                    )
                case "completed":
                    emb: nextcord.Embed = nextcord.Embed(
                        title=f"Список просмотренного ({animes_len}) | {user.display_name}"
                    )

            emb.colour = nextcord.Colour.green()
            if interaction.guild.icon:
                emb.set_thumbnail(url=interaction.guild.icon.url)

            for idx, items in enumerate(anime):
                emb.add_field(
                    name=f"{page * 10 + idx + 1}. 📺 {items.name}|{items.score}⭐",
                    value=f"💿 Эпизоды: {items.episodes}|{items.kind.capitalize()}",
                    inline=False,
                )
            if emb.fields:
                embs.append(emb)

        message: nextcord.Message = await interaction.followup.send(
            embed=embs[0], delete_after=300
        )

        paginator: Paginator = Paginator(
            message,
            embs,
            interaction.user,
            self.bot,
            footerpage=True,
            footerdatetime=False,
            footerboticon=True,
            timeout=180.0,
        )
        try:
            await paginator.start()
        except nextcord.errors.NotFound:
            pass

    @MilkCog.slash_command(
        description="Добавить свой ID в базу данных. Требуется URL аккаунта Shikimori",
    )
    async def shikimori_account_add(
        self,
        interaction: nextcord.Interaction,
        url: Optional[str] = nextcord.SlashOption(
            name="url", description="Ссылка на ваш профиль Shikimori", required=True
        ),
    ):
        if interaction.guild is None:
            return await interaction.send("Вы не находитесь на сервере!")
        await interaction.response.defer()

        if not url.startswith("https://shikimori.one/"):
            return await interaction.followup.send("Укажите URL-профиля Shikimori")

        page: requests.Response = requests.get(url=url, headers=headers)
        soup: BeautifulSoup = BeautifulSoup(page.text, "html.parser")
        a: Optional[BeautifulSoup] = soup.find("div", class_="profile-head")
        a: list[str] = str(a).split('">')
        pid: int = int(a[0].split('data-user-id="')[1])

        user: dict = api.users(pid).GET()

        emb: nextcord.Embed = nextcord.Embed(
            title=f"{interaction.user.display_name}, проверьте введённые данные"
        )

        emb.add_field(name="Никнейм", value=user["nickname"], inline=False)

        emb.set_thumbnail(url=user["avatar"])

        emb.colour = nextcord.Colour.blue()

        view: nextcord.ui.View = nextcord.ui.View()
        buttons: dict = {}
        for reaction in submit:
            button: nextcord.ui.Button = nextcord.ui.Button(
                style=nextcord.ButtonStyle.secondary, emoji=reaction
            )
            buttons[button.custom_id] = reaction
            view.add_item(button)

        msg: nextcord.Message = await interaction.followup.send(embed=emb, view=view)

        try:
            interaction: nextcord.Interaction = await self.bot.wait_for(
                "interaction",
                timeout=60.0,
                check=lambda m: m.user.id == interaction.user.id
                and m.message.id == msg.id
                # and str(m.emoji) in submit,
            )
        except asyncio.TimeoutError:
            emb.set_footer(text="Время вышло")
            emb.colour = nextcord.Colour.red()
            return await msg.edit(embed=emb)

        if buttons[interaction.data["custom_id"]] == "✅":

            try:
                self.bot.database.add_shikimori_profile(
                    id=interaction.user.id,
                    guild_id=interaction.guild.id,
                    shikimori_id=pid,
                )
            except Exception as e:
                await interaction.followup.send(f"Произошла ошибка: {e}")
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
