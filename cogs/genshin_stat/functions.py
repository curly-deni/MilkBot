import datetime

import nextcord
from nextcord.ext import commands
from nextcord.ext.commands import Context
import asyncio
import genshin
from nextcord_paginator.nextcord_paginator import Paginator
from typing import Union
from dataclasses import dataclass
from utils import list_split
from .ui import PaginationSelectors


def get_embed_template(
    nick: str, ar: Union[str, int], uid: Union[str, int], ctx: Context
) -> nextcord.Embed:
    embed = nextcord.Embed(
        description=f"Ник: {nick}\nРанг приключений: {ar}\nUID: {uid}",
        timestamp=datetime.datetime.now(),
        colour=nextcord.Colour.random(),
    )

    if ctx.author.avatar:
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
    else:
        embed.set_author(
            name=ctx.author.display_name,
            icon_url=f"https://cdn.discordapp.com/embed/avatars/{int(ctx.author.discriminator) % 5}.png",
        )

    return embed


teyvat_elements = {
    "geo": "Гео",
    "hydro": "Гидро",
    "pyro": "Пиро",
    "anemo": "Анемо",
    "cryo": "Крио",
    "electro": "Электро",
    "dendro": "Дендро",
}

submit = [
    "✅",
    "❌",
]


@dataclass
class ArtifactLine:
    title: str
    lvl: str
    set: str


@dataclass
class GenshinMember:
    name: str
    nick: str
    ar: int
    uid: int


class NewGenshinStat(commands.Cog, name="Статистика Genshin Impact"):
    """Статистика игроков сервера в Genshin Impact"""

    COG_EMOJI: str = "🎮"

    def __init__(self, bot):
        self.bot = bot
        self.genshin_client: genshin.Client = genshin.Client(
            dict(ltuid=bot.settings["ltuid"], ltoken=bot.settings["ltoken"]),
            lang="ru-ru",
            game=genshin.Game.GENSHIN,
        )

    @commands.command(brief="Список игроков с указанием UID и AR")
    @commands.guild_only()
    async def геншин_игроки(self, ctx: Context):

        users: list[GenshinMember] = []

        players: list = self.bot.database.get_genshin_players(ctx.guild.id)

        for player in players:
            try:
                member = ctx.guild.get_member(player.id)
                hoyolab_profile = await self.genshin_client.get_record_card(
                    player.hoyolab_id
                )

                users.append(
                    GenshinMember(
                        name=member.display_name,
                        nick=hoyolab_profile.nickname,
                        ar=int(hoyolab_profile.level),
                        uid=hoyolab_profile.uid,
                    )
                )
            except:
                continue

        if not users:
            return await ctx.send("Никто из участников сервера не добавил свой UID.")

        users.sort(key=lambda m: m.ar, reverse=True)
        users: list[list[GenshinMember]] = list_split(users)
        embs: list[nextcord.Embed] = []

        for page, user in enumerate(users):
            emb: nextcord.Embed = nextcord.Embed(
                title=f"Игроки Genshin Impact | {ctx.guild.name}",
                colour=nextcord.Colour.green(),
            )
            emb.set_thumbnail(url=ctx.guild.icon.url)

            for idx, items in enumerate(user):
                emb.add_field(
                    name=f"{page * 10 + idx + 1}. {items.name} | {items.nick}",
                    value=f"UID: {items.uid} | AR: {items.ar}",
                    inline=False,
                )
            if emb.fields:
                embs.append(emb)

        message: nextcord.Message = await ctx.send(embed=embs[0], delete_after=300)

        page = Paginator(
            message,
            embs,
            ctx.author,
            self.bot,
            footerpage=True,
            footerdatetime=False,
            footerboticon=False,
            timeout=0,
        )
        try:
            await page.start()
        except nextcord.errors.NotFound:
            pass

    @commands.command(
        brief="Вывод статистики игрока", aliases=["геншин_ранг", "витрина"]
    )
    @commands.guild_only()
    async def геншин_аккаунт(
        self, ctx: Context, пользователь: Union[str, nextcord.Member] = ""
    ):

        if isinstance(пользователь, nextcord.Member):
            user = пользователь
        elif пользователь == "":
            user = ctx.author
        else:
            try:
                user = ctx.guild.get_member(int(пользователь))
            except:
                user = ctx.author

        player = self.bot.database.get_genshin_profile(user.id, ctx.guild.id)

        if player is not None:
            card = await self.genshin_client.get_record_card(player.hoyolab_id)

            try:
                ar: int = card.level
            except:
                return await ctx.send(
                    f"{ctx.author.mention}, проверьте настройки приватности и/или привяжите genshin аккаунт"
                )

            uid: int = card.uid
            n = "\n"
            nick: str = card.nickname
            data: genshin.models.genshin.chronicle.stats.GenshinUserStats = (
                await self.genshin_client.get_genshin_user(uid)
            )
            main_embeds: dict = {}

            stat_embed = get_embed_template(nick, ar, uid, ctx)
            stats = data.stats
            stat_embed.add_field(
                name="Статистика",
                value=f"""**Дни активности:** {stats.days_active}
**Достижения:** {stats.achievements}
**Персонажи:** {stats.characters}
**Точки телепортации:** {stats.unlocked_waypoints}
**Анемокулы:** {stats.anemoculi}
**Геокулы:** {stats.geoculi}
**Электрокулы:** {stats.electroculi}
**Подземелья:** {stats.unlocked_domains}
**Прогресс Витой Бездны:** {stats.spiral_abyss}
**Роскошные сундуки:** {stats.luxurious_chests}
**Драгоценные сундуки**: {stats.precious_chests}
**Богатые сундуки:** {stats.exquisite_chests}
**Обычные сундуки:** {stats.common_chests}""",
            )

            character_embed = get_embed_template(nick, ar, uid, ctx)
            characters = data.characters
            character_embed.add_field(
                name="Персонажи",
                value="\n".join(
                    f"💠 **{character.name}** C{character.constellation} | {character.rarity} ⭐"
                    + f"\n**Стихия:** {teyvat_elements[character.element.lower()]}\n"
                    + f"**Уровень персонажа:** {character.level} | **Уровень дружбы:** {character.friendship}"
                    for character in characters
                ),
            )

            teapot_embed = get_embed_template(nick, ar, uid, ctx)
            teapot = data.teapot
            teapot_embed.add_field(
                name="Чайник безмятежности",
                value=f"""**Уровень доверия:** {teapot.level}
**Сила Адептов:** {teapot.comfort} ({teapot.comfort_name})
**Количество предметов:** {teapot.items}
**Количество посетителей:** {teapot.visitors}

**Доступные обители:**
{n.join(f"💠 {realm.name}" for realm in teapot.realms)}""",
            )

            explorations_embed = get_embed_template(nick, ar, uid, ctx)
            explorations: list = data.explorations
            explorations_checked: list = []
            for region in explorations:
                if region.name != "":
                    explorations_checked.append(region)
            explorations_embed.add_field(
                name="Прогресс исследования",
                value="\n".join(
                    f"💠 **{region.name}** - {float(region.explored)/10}%"
                    + (
                        f"""\n{n.join(f"**{offer.name}** - {offer.level} уровень" for offer in region.offerings)}"""
                        if region.offerings
                        else ""
                    )
                    for region in explorations_checked
                ),
            )
            main_embeds["Статистика"] = stat_embed
            main_embeds["Чайник безмятежности"] = teapot_embed
            main_embeds["Исследования"] = explorations_embed

            characters_embeds: dict = {}
            characters_embeds["Общая информация о персонажах"] = character_embed
            for character in characters:
                embed = get_embed_template(nick, ar, uid, ctx)
                embed.set_thumbnail(url=character.icon)

                embed.title = f"**{character.name}** C{character.constellation} | {character.rarity} ⭐"
                embed.add_field(
                    name=f"**{character.weapon.name}** R{character.weapon.refinement} | {character.weapon.rarity} ⭐",
                    value=f"Тип: {character.weapon.type.lower()}\n\n{character.weapon.description}",
                )

                artifact_sets: dict = {}
                artifact_sets_count: dict = {}

                artifact_sets_lines: list[list[ArtifactLine, int]] = []

                for artifact in character.artifacts:
                    match artifact.pos_name:
                        case "Цветок жизни":
                            emoji = "🌼"
                        case "Перо смерти":
                            emoji = "🪶"
                        case "Пески времени":
                            emoji = "⌛"
                        case "Кубок пространства":
                            emoji = "🏆"
                        case "Корона разума":
                            emoji = "👑"

                    artifact_sets[artifact.set.id] = artifact.set
                    if artifact.set.id in artifact_sets_count:
                        artifact_sets_count[artifact.set.id] += 1
                    else:
                        artifact_sets_count[artifact.set.id] = 1

                    artifact_sets_lines.append(
                        [
                            ArtifactLine(
                                title=f"{emoji} **{artifact.name}** | {artifact.rarity}⭐",
                                lvl=f"**Уровень:** {artifact.level}",
                                set=f"**Сет:** {artifact.set.name}",
                            ),
                            artifact.set.id,
                        ]
                    )

                if artifact_sets_lines:
                    set_bonus_line = ""

                    for aset in artifact_sets:
                        set_bonus_line += f"**{artifact_sets[aset].name}** ({artifact_sets_count[aset]})\n"
                        if 2 <= artifact_sets_count[aset] < 4:
                            set_bonus_line += (
                                artifact_sets[aset].effects[0].effect + "\n"
                            )
                        elif artifact_sets_count[aset] == 4:
                            set_bonus_line += (
                                artifact_sets[aset].effects[0].effect + "\n"
                            )
                        set_bonus_line += "\n"

                    if set_bonus_line == "":
                        set_bonus_line = "Отсутствует"

                    embed.add_field(name="Бонус сета", value=set_bonus_line)

                    embed.add_field(name="\u200b", value="\u200b")

                for artifact in artifact_sets_lines:
                    embed.add_field(
                        name=artifact[0].title,
                        value=f"{artifact[0].lvl}\n{artifact[0].set} ({artifact_sets_count[artifact[1]]})",
                    )

                if not artifact_sets_lines:
                    embed.add_field(
                        name="\u200b", value="**Артефактов не обнаружено!**"
                    )

                characters_embeds[character.name] = embed

            message: nextcord.Message = await ctx.send(
                "Подождите, операция выполняется"
            )

            view = PaginationSelectors(
                message, ctx.author, main_embeds, characters_embeds
            )

            await message.edit(content=None, embed=main_embeds["Статистика"], view=view)
        else:
            return await ctx.send("Выбранного UID нет в базе!")

    @commands.command(brief="Добавить свой HoYoLab ID в базу данных сервера")
    @commands.guild_only()
    async def геншин_добавить(self, ctx: Context, *, hoyolab_id: str = ""):

        if hoyolab_id == "":
            m1 = await ctx.send(f"{ctx.author.mention}, напишите ваш HoYoLab ID.")
            try:
                msg = await self.bot.wait_for(
                    "message",
                    timeout=60.0,
                    check=lambda m: m.channel == ctx.channel
                    and m.author.id == ctx.author.id,
                )
                e = msg.content
            except asyncio.TimeoutError:
                await m1.delete()
                return
        else:
            e = hoyolab_id

        try:
            card = await self.genshin_client.get_record_card(int(e))
        except:
            return await ctx.send(f"{ctx.author.mention}, ваш HoYoLab ID неверен.")

        try:
            ar = card.level
        except:
            return await ctx.send(
                f"{ctx.author.mention}, проверьте настройки приватности и/или привяжите genshin аккаунт"
            )

        uid = card.uid
        nickname = card.nickname

        emb: nextcord.Embed = nextcord.Embed(
            title=f"{ctx.author.display_name}, проверьте введённые данные",
            colour=nextcord.Colour.blue(),
        )
        emb.add_field(name="Ник", value=nickname)

        emb.add_field(name="Ранг приключений", value=ar)

        emb.add_field(name="UID", value=uid, inline=False)

        view: nextcord.ui.View = nextcord.ui.View()
        buttons: dict = {}
        for reaction in submit:
            button: nextcord.ui.Button = nextcord.ui.Button(
                style=nextcord.ButtonStyle.secondary, emoji=reaction
            )
            buttons[button.custom_id] = reaction
            view.add_item(button)

        msg: nextcord.Message = await ctx.send(embed=emb, view=view)

        try:
            interaction: nextcord.Interaction = await self.bot.wait_for(
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

            profile = self.bot.database.get_genshin_profile(ctx.author.id, ctx.guild.id)

            if profile is None:
                self.bot.database.add_genshin_profile(
                    id=ctx.author.id,
                    guild_id=ctx.guild.id,
                    hoyolab_id=int(hoyolab_id),
                    genshin_id=int(uid),
                )
            else:
                profile.hoyolab_id = int(hoyolab_id)
                profile.genshin_id = int(uid)
                self.bot.database.session.commit()

            emb.title = "Успешно добавлено"
            emb.colour = nextcord.Colour.brand_green()
            await msg.edit(embed=emb, view=None)
        else:
            emb.title = "Отменено"
            emb.colour = nextcord.Colour.red()
            await msg.edit(embed=emb, view=None)


def setup(bot):
    bot.add_cog(NewGenshinStat(bot))
