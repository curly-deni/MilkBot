import datetime
import nextcord
from nextcord.ext import commands
from nextcord.utils import get
from nextcord.ext.commands import Context

import database
from checkers import check_editor_permission
from typing import Union

from nextcord_paginator import Paginator

from sqlalchemy import desc
from utils import list_split


class Stats(commands.Cog, name="Статистика"):
    """Статистика пользователей сервера"""

    COG_EMOJI: str = "📓"

    def __init__(self, bot):
        self.bot = bot

    def cog_check(self, ctx: Context) -> bool:
        return ctx.message.guild.id != 876474448126050394

    @commands.command(
        pass_context=True, brief="Статистика пользователя", aliases=["ранг", "rank"]
    )
    @commands.guild_only()
    async def аккаунт(
        self, ctx: Context, пользователь: Union[nextcord.Member, str] = ""
    ):

        if isinstance(пользователь, nextcord.Member):
            user = пользователь
        else:
            user = ctx.author

        user_info: database.GuildsStatistics = self.bot.database.get_member_statistics(
            user.id, ctx.guild.id
        )

        embed: nextcord.Embed = nextcord.Embed(
            timestamp=datetime.datetime.now(),
            description=f"""*{user_info.citation if user_info.citation is not None and user_info.citation != "" else "установка цитаты по команде =цитата"}*\n
**Дата вступления на сервер:** {nextcord.utils.format_dt(user.joined_at, 'f')}""",
        )

        if user.avatar:
            embed.set_author(name=user.display_name, icon_url=user.avatar.url)
        else:
            embed.set_author(
                name=user.display_name,
                icon_url=f"https://cdn.discordapp.com/embed/avatars/{str(int(user.discriminator) % 5)}.png",
            )

        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)

        peoples_undefined: list = self.bot.database.get_all_members_statistics(
            ctx.guild.id
        )  # .sort(key=lambda people: people.xp)
        peoples: list[int] = []
        for people in peoples_undefined:
            member = get(ctx.guild.members, id=people.id)
            if member is not None:
                peoples.append(member.id)

        embed.add_field(
            name="Валюты", value=f"✨: {user_info.gems}\n🪙: {user_info.coins}"
        )
        embed.add_field(
            name="Статистика",
            value=f"**Уровень:** {user_info.lvl}\n**Опыт:** {user_info.xp}\n**Место в топе:** {peoples.index(user.id)+1}",
        )

        voice_str = ""
        if user_info.voice_time is not None:
            hours: str = str(user_info.voice_time // 3600)
            minutes: Union[int, str] = (user_info.voice_time % 3600) // 60
            if minutes < 10:
                minutes = "0" + str(minutes)
            seconds: Union[int, str] = (user_info.voice_time % 3600) % 60
            if seconds < 10:
                seconds = "0" + str(seconds)

            if hours == "0":
                voice_str: str = f"\n:microphone:: {minutes}:{seconds}"
            else:
                voice_str: str = f"\n:microphone:: {hours}:{minutes}:{seconds}"

        embed.add_field(
            name="Активность", value=f":cookie:: {user_info.cookies}{voice_str}"
        )

        # sending image to discord channel
        await ctx.send(embed=embed)

    @commands.command(brief="Топ пользователей сервера", aliases=["top"])
    @commands.guild_only()
    async def лидеры(self, ctx: Context):

        peoples_undefined: list = self.bot.database.get_all_members_statistics(ctx.guild.id)
        peoples: list[list] = []

        for people in peoples_undefined:
            member: Union[nextcord.Member, None] = ctx.guild.get_member(people.id)
            if member is not None:
                if not member.bot:
                    peoples.append([member, people])

        peoples = list_split(peoples)

        embs: list[nextcord.Embed] = []
        for page, people_list in enumerate(peoples):
            emb = nextcord.Embed(title=f"Топ пользователей | {ctx.guild.name}")
            emb.colour = nextcord.Colour.green()
            emb.set_thumbnail(url=ctx.guild.icon.url)

            for idx, items in enumerate(people_list):
                if items[1].lvl is not None:
                    strx = f"**Уровень:** {items[1].lvl} | "
                else:
                    strx = f"**Уровень:** 0 | "

                if items[1].xp is not None:
                    strx += f"**Опыт:** {items[1].xp} | "
                else:
                    strx += f"**Опыт:** 0 | "

                if items[1].cookies is not None:
                    if items[1].cookies != 0:
                        strx += f":cookie:: {items[1].cookies} | "

                if items[1].gems is not None:
                    if items[1].gems != 0:
                        strx += f":sparkles:: {items[1].gems} | "

                if items[1].coins is not None:
                    if items[1].coins != 0:
                        strx += f":coin:: {items[1].coins} | "

                if items[1].voice_time is not None:
                    if items[1].voice_time != 0:
                        hours: str = str(items[1].voice_time // 3600)
                        minutes: Union[int, str] = (items[1].voice_time % 3600) // 60
                        if minutes < 10:
                            minutes = "0" + str(minutes)
                        seconds: Union[int, str] = (items[1].voice_time % 3600) % 60
                        if seconds < 10:
                            seconds = "0" + str(seconds)

                        if hours != "0":
                            strx += f":microphone:: {hours}:{minutes}:{seconds}"
                        else:
                            strx += f":microphone:: {minutes}:{seconds}"

                name: str = items[0].display_name

                emb.add_field(
                    name=f"{page*10 + idx + 1}. {name}",
                    value=strx,
                    inline=False,
                )
            if emb.fields:
                embs.append(emb)

        message: nextcord.Message = await ctx.send(embed=embs[0])

        page: Paginator = Paginator(
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
        brief="Получение списка гемов у пользователей",
    )
    @commands.check(check_editor_permission)
    @commands.guild_only()
    async def gems_list(
        self,
        ctx: Context,
    ):
        embed: nextcord.Embed = nextcord.Embed(
            title="Cтатистика по гемам",
            colour=nextcord.Colour.random(),
            timestamp=datetime.datetime.now(),
            description="",
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

        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)

        peoples_undefined: list = (
            self.bot.database.session.query(database.GuildsStatistics)
            .filter(database.GuildsStatistics.guild_id == ctx.guild.id)
            .order_by(desc(database.GuildsStatistics.gems))
        )
        if peoples_undefined:
            for people in peoples_undefined:
                member: Union[nextcord.Member, None] = ctx.guild.get_member(people.id)
                if member is not None and people.gems > 0:
                    embed.description += (
                        f"**{member.display_name}** - {people.gems} :sparkles:\n"
                    )

        await ctx.send(embed=embed)

    @commands.command(
        pass_context=True,
        aliases=[f"шар", "звездочки"],
        brief="Редактирование количества монет пользователя",
    )
    @commands.check(check_editor_permission)
    @commands.guild_only()
    async def gems(
        self,
        ctx: Context,
        пользователь: Union[nextcord.Member, str] = "",
        количество: int = 0,
    ):

        if not isinstance(пользователь, nextcord.Member):
            return await ctx.send(
                f"{ctx.author.mention}, отметьте пользователя и кол-во гемов, которые вы ему добавите!"
            )
        else:
            if количество == 0:
                return await ctx.send(
                    f"{ctx.author.mention}, отметьте пользователя и кол-во гемов, которые вы ему добавите!"
                )

            self.bot.database.add_gems(
                id=пользователь.id, guild_id=ctx.guild.id, coins=количество
            )
            await ctx.send(f"{ctx.author.mention}, изменено!")

    @commands.command(brief="Установка цитаты для статистики")
    @commands.guild_only()
    async def цитата(self, ctx: Context, *, цитата: str = ""):

        if цитата == "":
            await ctx.send(f"{ctx.author.mention}, отсутствует цитата")
        else:
            member_info: database.GuildsStatistics = (
                self.bot.database.get_member_statistics(ctx.author.id, ctx.guild.id)
            )
            member_info.citation = цитата
            self.bot.database.session.commit()
            await ctx.send(f"{ctx.author.mention}, успешно заменено!")


def setup(bot):
    bot.add_cog(Stats(bot))
