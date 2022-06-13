import datetime

import nextcord
from nextcord.ext import commands
from nextcord.ext.commands import Context
import asyncio
import genshinstats as gs
from nextcord_paginator.nextcord_paginator import Paginator
from typing import Union
from dataclasses import dataclass
from utils import list_split

submit = [
    "✅",
    "❌",
]


@dataclass
class GenshinMember:
    name: str
    nick: str
    ar: int
    uid: int


class Genshin(commands.Cog, name="Статистика Genshin Impact"):
    """Статистика игроков сервера в Genshin Impact"""

    COG_EMOJI: str = "🎮"

    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Список игроков с указанием UID и AR")
    @commands.guild_only()
    async def игроки(self, ctx: Context):

        users = []

        players = self.bot.database.get_genshin_players(ctx.guild.id)

        for player in players:
            try:
                member = ctx.guild.get_member(player.id)
                hoyolab_profile = gs.get_record_card(player.hoyolab_id)

                users.append(
                    GenshinMember(
                        name=member.display_name,
                        nick=hoyolab_profile["nickname"],
                        ar=int(hoyolab_profile["level"]),
                        uid=hoyolab_profile["game_role_id"],
                    )
                )
            except:
                continue

        if not users:
            return await ctx.send("Никто из участников сервера не добавил свой UID.")

        users.sort(key=lambda m: m.ar, reverse=True)
        users = list_split(users)
        embs = []

        for page, user in enumerate(users):
            emb = nextcord.Embed(
                title=f"Игроки Genshin Impact | {ctx.guild.name}",
                colour=nextcord.Colour.green(),
            )
            emb.set_thumbnail(url=ctx.guild.icon.url)

            for idx, items in enumerate(user):
                emb.add_field(
                    name=f"{page*10+idx+1}. {items.name} | {items.nick}",
                    value=f"UID: {items.uid} | AR: {items.ar}",
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
            footerdatetime=True,
            footerboticon=True,
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
            card = gs.get_record_card(player.hoyolab_id)

            try:
                ar = card["level"]
            except:
                return await ctx.send(
                    f"{ctx.author.mention}, проверьте настройки приватности и/или привяжите genshin аккаунт"
                )

            uid = card["game_role_id"]
            nick = card["nickname"]
            data = gs.get_user_stats(int(uid), lang="ru-ru")

            embed = nextcord.Embed(
                description=f"Ник: {nick}\nРанг приключений: {ar}\nUID: {uid}",
                timestamp=datetime.datetime.now(),
                colour=nextcord.Colour.random(),
            )

            if ctx.author.avatar:
                embed.set_author(
                    name=ctx.author.display_name, icon_url=ctx.author.avatar.url
                )
            else:
                embed.set_author(
                    name=ctx.author.display_name,
                    icon_url=f"https://cdn.discordapp.com/embed/avatars/{str(int(ctx.author.discriminator) % 5)}.png",
                )

            stats = data["stats"]
            n = "\n"
            embed.add_field(
                name="Статистика",
                value=f"""**Дни активности:** {stats['active_days']}
**Достижения:** {stats['achievements']}
**Персонажи:** {stats['characters']}
**Точки телепортации:** {stats['unlocked_waypoints']}
**Анемокулы:** {stats['anemoculi']}
**Геокулы:** {stats['geoculi']}
**Электрокулы:** {stats['electroculi']}
**Подземелья:** {stats['unlocked_domains']}
**Прогресс Витой Бездны:** {stats['spiral_abyss']}
**Роскошные сундуки:** {stats['luxurious_chests']}
**Драгоценные сундуки**: {stats['precious_chests']}
**Богатые сундуки:** {stats['exquisite_chests']}
**Обычные сундуки:** {stats['common_chests']}""",
                # inline=False
            )

            characters = data["characters"]
            embed.add_field(
                name="Персонажи",
                value=f"""{n.join(f"💠 **{character['name']}** | {character['rarity']} ⭐{n}**Уровень персонажа:** {character['level']} | **Уровень дружбы:** {character['friendship']}" for character in characters)}""",
            )

            teapot = data["teapot"]
            embed.add_field(
                name="Чайник безмятежности",
                value=f"""**Уровень доверия:** {teapot['level']}
**Сила Адептов:** {teapot['comfort']} ({teapot['comfort_name']})
**Количество предметов:** {teapot['items']}
**Количество посетителей:** {teapot['visitors']}

**Доступные обители:**
{n.join(f"💠 {realm['name']}" for realm in teapot['realms'])}""",
            )

            explorations = data["explorations"]
            explorations_checked = []
            for region in explorations:
                if region["name"] != "":
                    explorations_checked.append(region)
            embed.add_field(
                name="Прогресс исследования",
                value=f"""{n.join(f'''💠 **{region['name']}** - {region['explored']}%{f"{n}**Уровень репутации:** {region['level']}" if region['type'] == 'Reputation' else ''}{f"{n}{n.join('**' + offer['name'] + '** - ' + str(offer['level']) + ' уровень' for offer in region['offerings'])}" if region['offerings'] else ''}''' for region in explorations_checked)}""",
            )

            return await ctx.send(embed=embed)
        else:
            return await ctx.send("Выбранного UID нет в базе!")

    @commands.command(brief="Добавить свой HoYoLab ID в базу данных сервера")
    @commands.guild_only()
    async def геншин_добавить(self, ctx: Context, *, hoyolab_id: str = ""):

        if hoyolab_id is None:
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
            card = gs.get_record_card(int(e))
        except:
            return await ctx.send(f"{ctx.author.mention}, ваш HoYoLab ID неверен.")

        try:
            ar = card["level"]
        except:
            return await ctx.send(
                f"{ctx.author.mention}, проверьте настройки приватности и/или привяжите genshin аккаунт"
            )

        uid = card["game_role_id"]
        nickname = card["nickname"]

        emb = nextcord.Embed(
            title=f"{ctx.author.display_name}, проверьте введённые данные",
            colour=nextcord.Colour.blue(),
        )
        emb.add_field(name="Ник", value=nickname)

        emb.add_field(name="Ранг приключений", value=ar)

        emb.add_field(name="UID", value=uid, inline=False)

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

            self.bot.database.add_genshin_profile(
                id=ctx.author.id,
                guild_id=ctx.guild.id,
                hoyolab_id=int(hoyolab_id),
                genshin_id=int(uid),
            )
            emb.title = "Успешно добавлено"
            emb.colour = nextcord.Colour.brand_green()
            await msg.edit(embed=emb, view=None)
        else:
            emb.title = "Отменено"
            emb.colour = nextcord.Colour.red()
            await msg.edit(embed=emb, view=None)


def setup(bot):
    bot.add_cog(Genshin(bot))
    gs.set_cookie(ltuid=bot.settings["ltuid"], ltoken=bot.settings["ltoken"])
