import datetime

import nextcord
from nextcord.ext import commands
import enkanetwork
from enkanetwork import EnkaNetworkAPI
import asyncio
import modules.genshin as genshin
from nextcord_paginator.nextcord_paginator import Paginator
from typing import Union, Optional
from dataclasses import dataclass
from modules.utils import list_split
from .ui import PaginationSelectors


def get_embed_template(
    nick: str,
    ar: Union[str, int],
    uid: Union[str, int],
    interaction: nextcord.Interaction,
    icon: Optional[str] = None,
    sign: Optional[str] = None,
) -> nextcord.Embed:
    embed = nextcord.Embed(
        title=f"{nick} {ar} AR",
        description=f"*{sign}*" if sign is not None else "",
        timestamp=datetime.datetime.now(),
        colour=nextcord.Colour.random(),
    )

    embed.set_footer(text=f"UID: {uid}")

    if icon is not None:
        embed.set_thumbnail(url=icon)

    if interaction.user.avatar:
        embed.set_author(
            name=interaction.user.display_name, icon_url=interaction.user.avatar.url
        )
    else:
        embed.set_author(
            name=interaction.user.display_name,
            icon_url=f"https://cdn.discordapp.com/embed/avatars/{int(interaction.user.discriminator) % 5}.png",
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
        if self.bot.bot_type != "helper":
            self.genshin_client: genshin.Client = genshin.Client(
                dict(ltuid=bot.settings["ltuid"], ltoken=bot.settings["ltoken"]),
                lang="ru-ru",
                game=genshin.Game.GENSHIN,
            )
            self.enka_client: EnkaNetworkAPI = EnkaNetworkAPI()

    @nextcord.slash_command(
        guild_ids=[], force_global=True, description="Список игроков в Genshin Impact"
    )
    async def genshin_players(self, interaction: nextcord.Interaction):
        if interaction.guild is None:
            return await interaction.send("Вы на находитесь на сервере!")
        await interaction.response.defer(ephemeral=True)

        users: list[GenshinMember] = []

        players: list = self.bot.database.get_genshin_players(interaction.guild.id)

        for player in players:
            try:
                member = interaction.guild.get_member(player.id)
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
            return await interaction.followup.send(
                "Никто из участников сервера не добавил свой UID."
            )

        users.sort(key=lambda m: m.ar, reverse=True)
        users: list[list[GenshinMember]] = list_split(users)
        embs: list[nextcord.Embed] = []

        for page, user in enumerate(users):
            emb: nextcord.Embed = nextcord.Embed(
                title=f"Игроки Genshin Impact | {interaction.guild.name}",
                colour=nextcord.Colour.green(),
            )
            try:
                emb.set_thumbnail(url=interaction.guild.icon.url)
            except:
                pass

            for idx, items in enumerate(user):
                emb.add_field(
                    name=f"{page * 10 + idx + 1}. {items.name} | {items.nick}",
                    value=f"UID: {items.uid} | AR: {items.ar}",
                    inline=False,
                )
            if emb.fields:
                embs.append(emb)

        message = await interaction.followup.send(embed=embs[0])

        page = Paginator(
            message,
            embs,
            interaction.user,
            self.bot,
            footerpage=True,
            footerdatetime=False,
            footerboticon=False,
            timeout=180.0,
        )
        try:
            await page.start()
        except nextcord.errors.NotFound:
            pass

    @nextcord.slash_command(
        guild_ids=[],
        force_global=True,
        description="Информация об аккаунте в Genshin Impact",
    )
    async def genshin_account(
        self,
        interaction: nextcord.Interaction,
        пользователь: Optional[nextcord.Member] = nextcord.SlashOption(required=False),
    ):
        if interaction.guild is None:
            return await interaction.send("Вы на находитесь на сервере!")
        await interaction.response.defer()

        if isinstance(пользователь, nextcord.Member):
            user = пользователь
        else:
            user = interaction.user

        player = self.bot.database.get_genshin_profile(user.id, interaction.guild.id)

        if player is not None:
            uid = player.genshin_id
            n = "\n"
            main_embeds: dict = {}

            await self.enka_client.set_language(enkanetwork.Language("ru"))
            genshin_data: genshin.models.genshin.chronicle.stats.GenshinUserStats = (
                await self.genshin_client.get_genshin_user(uid)
            )
            enka_data = await self.enka_client.fetch_user(uid)

            nick = enka_data.player.nickname
            ar = enka_data.player.level
            sign = enka_data.player.signature
            icon = enka_data.player.icon.url

            stat_embed = get_embed_template(nick, ar, uid, interaction, icon, sign)
            stats = genshin_data.stats
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

            stat_embed.set_image(url=enka_data.player.namecard.banner)

            character_embed = get_embed_template(nick, ar, uid, interaction, icon, sign)
            characters = enka_data.characters
            if characters:
                character_embed.add_field(
                    name="Персонажи",
                    value="\n".join(
                        f"💠 **{character.name}** C{character.constellations_unlocked} | {character.ascension} ⭐"
                        + f"\n**Стихия:** {teyvat_elements[character.element.lower()]}\n"
                        + f"**Уровень персонажа:** {character.level} | **Уровень дружбы:** {character.friendship_level}"
                        for character in characters
                    ),
                )

            teapot_embed = get_embed_template(nick, ar, uid, interaction, icon, sign)
            teapot = genshin_data.teapot
            teapot_embed.add_field(
                name="Чайник безмятежности",
                value=f"""**Уровень доверия:** {teapot.level}
        **Сила Адептов:** {teapot.comfort} ({teapot.comfort_name})
        **Количество предметов:** {teapot.items}
        **Количество посетителей:** {teapot.visitors}

        **Доступные обители:**
        {n.join(f"💠 {realm.name}" for realm in teapot.realms)}""",
            )

            explorations_embed = get_embed_template(
                nick, ar, uid, interaction, icon, sign
            )
            explorations = genshin_data.explorations
            explorations_checked: list = []
            for region in explorations:
                if region.name != "":
                    explorations_checked.append(region)
            explorations_embed.add_field(
                name="Прогресс исследования",
                value="\n".join(
                    f"💠 **{region.name}** - {float(region.explored)}%"
                    + (
                        f"""\n{n.join(f"**{offer.name if offer.name != 'Reputation' else 'Репутация'}** - {offer.level} уровень" for offer in region.offerings)}"""
                        if region.offerings
                        else ""
                    )
                    for region in explorations_checked
                ),
            )
            main_embeds["Основные сведения"] = stat_embed
            main_embeds["Чайник безмятежности"] = teapot_embed
            main_embeds["Исследования"] = explorations_embed

            characters_embeds: dict = {}
            if characters:
                characters_embeds["Общая информация о персонажах"] = character_embed
                for character in characters:
                    embed = get_embed_template(
                        nick, ar, uid, interaction, character.image.icon
                    )
                    embed.set_image(url=character.image.banner)
                    skills = [str(skill.level) for skill in character.skills]

                    embed.title = (
                        f"**{character.name}** C{character.constellations_unlocked}"
                    )
                    embed.add_field(
                        name="Характеристики:",
                        value=f"""**Уровень персонажа:** {character.level}/{character.max_level}
    **Уровень дружбы:** {character.friendship_level}
    **Таланты:** {'|'.join(skills)}
    **HP:** {character.stats.FIGHT_PROP_MAX_HP.to_rounded()}
    **ATK:** {character.stats.FIGHT_PROP_CUR_ATTACK.to_rounded()}
    **DEF:** {character.stats.FIGHT_PROP_CUR_DEFENSE.to_rounded()}
    **МС:** {character.stats.FIGHT_PROP_ELEMENT_MASTERY.to_rounded()}
    **Шанс крит. урона:** {character.stats.FIGHT_PROP_CRITICAL.to_percentage_symbol()}
    **Крит. урон:** {character.stats.FIGHT_PROP_CRITICAL_HURT.to_percentage_symbol()}""",
                    )

                    for artifact in character.equipments:
                        if str(artifact.type).find("ARTIFACT") == -1:
                            embed.add_field(
                                name=f"{artifact.detail.name} R{artifact.refinement} {artifact.detail.rarity}*",
                                value=(
                                    f"**Уровень:** {artifact.level}"
                                    + f"\n**{artifact.detail.mainstats.name}** {artifact.detail.mainstats.value}{'%' if str(artifact.detail.mainstats.type).find('PERCENT') != -1 else ''}"
                                    + "\n"
                                    + "\n".join(
                                        [
                                            f"**{substat.name}** +{substat.value}{'%' if str(substat.type).find('PERCENT') != -1 else ''}"
                                            for substat in artifact.detail.substats
                                        ]
                                    )
                                ),
                            )

                    for artifact in character.equipments:
                        if str(artifact.type).find("ARTIFACT") != -1:
                            emoji = ""
                            match artifact.detail.artifact_type:
                                case "Flower":
                                    emoji = "🌼 "
                                case "Feather":
                                    emoji = "🪶 "
                                case "Sands":
                                    emoji = "⌛ "
                                case "Goblet":
                                    emoji = "🏆 "
                                case "Circlet":
                                    emoji = "👑 "

                            embed.add_field(
                                name=f"{emoji}{artifact.detail.name} {artifact.detail.rarity}*",
                                value=(
                                    f"**Сет:** {artifact.detail.artifact_name_set}"
                                    + f"\n**Уровень:** {artifact.level}"
                                    + f"\n**{artifact.detail.mainstats.name}** +{artifact.detail.mainstats.value}{'%' if str(artifact.detail.mainstats.type).find('PERCENT') != -1 else ''}"
                                    + "\n"
                                    + "\n".join(
                                        [
                                            f"**{substat.name}** +{substat.value}{'%' if str(substat.type).find('PERCENT') != -1 else ''}"
                                            for substat in artifact.detail.substats
                                        ]
                                    )
                                ),
                                inline=False,
                            )

                    characters_embeds[character.name] = embed

            message: nextcord.Message = await interaction.followup.send(
                f"Статистика пользователя {user.name} в Genshin Impact"
            )

            view = PaginationSelectors(
                message, interaction.user, main_embeds, characters_embeds
            )

            if characters:
                await message.edit(
                    content=None, embed=main_embeds["Основные сведения"], view=view
                )
            else:
                await message.edit(
                    content="**У данного аккаунта скрыты детали персонажей, функциональность ограничена.**",
                    embed=main_embeds["Основные сведения"],
                    view=view,
                )
            await view.wait()
        else:
            return await interaction.followup.send("Выбранного UID нет в базе!")

    @nextcord.slash_command(
        guild_ids=[],
        force_global=True,
        description="Добавить свой HoYoLab ID в базу данных сервера",
    )
    async def genshin_account_add(
        self,
        interaction: nextcord.Interaction,
        genshin_id: Optional[int] = nextcord.SlashOption(required=True),
    ):
        if interaction.guild is None:
            return await interaction.send("Вы на находитесь на сервере!")
        await interaction.response.defer(ephemeral=True)

        try:
            enka_data = await self.enka_client.fetch_user(genshin_id)
        except:
            return await interaction.followup.send(
                f"{interaction.user.mention}, ваш UID неверен."
            )

        try:
            ar = enka_data.player.level
        except:
            return await interaction.followup.send(
                f"{interaction.user.mention}, проверьте настройки приватности и/или привяжите genshin аккаунт"
            )

        emb: nextcord.Embed = nextcord.Embed(
            title=f"{interaction.user.display_name}, проверьте введённые данные",
            colour=nextcord.Colour.blue(),
        )
        emb.set_thumbnail(url=enka_data.player.icon.url)
        emb.set_image(url=enka_data.player.namecard.banner)

        emb.description = f"""**{enka_data.player.nickname} {enka_data.player.level} AR**
*{enka_data.player.signature}*"""

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
            return await msg.edit(embed=emb, view=None)

        if buttons[interaction.data["custom_id"]] == "✅":

            profile = self.bot.database.get_genshin_profile(
                interaction.user.id, interaction.guild.id
            )

            if profile is None:
                self.bot.database.add_genshin_profile(
                    id=interaction.user.id,
                    guild_id=interaction.guild.id,
                    genshin_id=genshin_id,
                )
            else:
                profile.genshin_id = genshin_id
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
