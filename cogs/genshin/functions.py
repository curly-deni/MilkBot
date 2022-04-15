# for discord
import nextcord
from nextcord.utils import get
import asyncio
from nextcord.ext import commands, tasks
from settings import settings

# for logs
import asyncio
from time import time
from datetime import datetime

# for database
import database.genshin as genshin
from database.db_classes import getGenshinClass
import genshinstats as gs

uri = settings["StatUri"]


submit = [
    "✅",
    "❌",
]

# for card
from card.genshin import *
import unicodedata

# for multipage embed
from nextcord_paginator import paginator as Paginator

# for cards
from settings import banners  # name of cards
from settings import colors  # name of colors from Pillow

gs.set_cookie(ltuid=settings["ltuid"], ltoken=settings["ltoken"])


def massive_split(mas):
    masx = []
    l10 = len(mas) // 10
    for i in range(l10 + 1):
        masx.append(mas[i * 10 : (i + 1) * 10])
    return masx


class Genshins(commands.Cog, name="Статистика Genshin Impact"):
    """Статистика игроков сервера в Genshin Impact"""

    COG_EMOJI = "🎮"

    def __init__(self, bot):
        self.bot = bot
        self.update.start()

    @tasks.loop(seconds=3600)
    async def update(self):

        for guild in self.bot.guilds:

            Genshin = getGenshinClass(guild.id)

            try:
                x = self.bot.databaseSession.query(Genshin).all()
            except:
                x = []

            for xe in x:
                try:
                    member = await guild.fetch_member(xe.uid)
                except:
                    member = None
                    pass

                if member is not None:
                    card = gs.get_record_card(int(xe.mihoyouid))

                    try:
                        xe.ar = card["level"]
                    except:
                        xe.ar = None
                        pass

                    if xe.ar is not None:
                        xe.genshinname = card["nickname"]
                        xe.discordname = member.display_name
                        xe.genshinuid = card["game_role_id"]

                self.bot.databaseSession.commit()

    @commands.command(pass_context=True, brief="Список игроков с указанием UID и AR")
    @commands.guild_only()
    async def игроки(self, ctx):

        user = []

        # if not connected to database

        Genshin = getGenshinClass(ctx.guild.id)

        x = self.bot.databaseSession.query(Genshin).all()

        for xe in x:
            if xe.genshinuid is not None:
                user.append(xe)

        if user == []:
            await ctx.send("Никто из участников сервера не добавил свой UID.")
            return
        user = massive_split(user)
        embs = []

        c = 0
        for u in user:
            emb = nextcord.Embed(title=f"Игроки Genshin Impact | {ctx.guild.name}")
            emb.color = nextcord.Colour.green()
            emb.set_thumbnail(url=ctx.guild.icon.url)

            for idx, items in enumerate(u):
                emb.add_field(
                    name=f"{c*10+idx+1}. {items.discordname} | {items.genshinname}",
                    value=f"UID: {items.genshinuid} | AR: {items.ar}",
                    inline=False,
                )

            embs.append(emb)
            c += 1

        try:
            await ctx.message.delete()
            pass
        except nextcord.errors.Forbidden:
            pass

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

    @commands.command(pass_context=True, brief="Витрина с персонажами")
    @commands.guild_only()
    async def витрина(self, ctx, пользователь=None):

        usr = пользователь
        # check user input
        if usr is None:
            user = ctx.author
        else:
            if not usr.startswith("<"):
                try:
                    user = await ctx.guild.fetch_member(usr)
                except:
                    return await ctx.send("Неверный ввод")
            else:
                try:
                    user = ctx.message.mentions[0]
                    pass
                except:
                    return await ctx.send("Неверный ввод!")

        # if not connected to database

        x = genshin.getInfo(self.bot.databaseSession, ctx.guild.id, user.id)

        if x is not None:
            card = gs.get_record_card(x.mihoyouid)
            try:
                ar = card["level"]
                pass
            except:
                await ctx.send(
                    f"{user.mention}, проверьте настройки приватности и/или привяжите genshin аккаунт"
                )

            uid = card["game_role_id"]
            data = gs.get_user_stats(int(uid), lang="ru-ru")
            characters = data["characters"]

            cardx = board(characters)
            cardx.avatar = user.avatar.url
            cardx.uid = uid
            cardx.ar = ar
            cardx.genshinname = f"{card['nickname']} UID: {uid}"

            cardx.color = x.color_stat
            cardx.namecolor = x.color_name
            cardx.statcolor = x.color_titles
            cardx.path = x.background

        else:
            await ctx.send("Выбранного UID нет в базе!")
            return False

        # sending image to discord channel
        await ctx.send(file=await cardx.create())
        await ctx.send(f"UID: {uid}")

    @commands.command(pass_context=True, brief="Вывод статистики игрока")
    @commands.guild_only()
    async def геншин_ранг(self, ctx, пользователь=None):

        usr = пользователь
        # check user input
        if usr is None:
            user = ctx.author
        else:
            if not usr.startswith("<"):
                try:
                    user = await ctx.guild.fetch_member(usr)
                except:
                    return await ctx.send("Неверный ввод")
            else:
                try:
                    user = ctx.message.mentions[0]
                    pass
                except:
                    return await ctx.send("Неверный ввод!")

        # if not connected to database

        x = genshin.getInfo(self.bot.databaseSession, ctx.guild.id, user.id)

        if x is not None:
            card1 = rank()

            card1.avatar = user.avatar.url

            card1.name = unicodedata.normalize("NFKC", str(user.display_name))

            card1.color = x.color_stat
            card1.namecolor = x.color_name
            card1.statcolor = x.color_titles

            card1.path = x.background
            card = gs.get_record_card(int(x.mihoyouid))

            try:
                card1.ar = card["level"]
                pass
            except:
                await ctx.send(
                    f"{ctx.author.mention}, проверьте настройки приватности и/или привяжите genshin аккаунт"
                )

            uid = card["game_role_id"]
            card1.genshinname = f"{card['nickname']} UID: {uid}"

            data = gs.get_user_stats(int(uid), lang="ru-ru")

            stats = data["stats"]
            for field, value in stats.items():
                exec(f"card1.{field} = '{value}'")
        else:
            await ctx.send("Выбранного UID нет в базе!")
            return False

        # sending image to discord channel
        await ctx.send(file=await card1.create())
        await ctx.send(f"UID: {uid}")

    @commands.command(pass_context=True, brief="Выбор цвета для статистики и витрины")
    @commands.guild_only()
    async def геншин_цвет(self, ctx, *цвета):

        args = цвета
        # if user input blank > send colors magazine
        if args == ():
            embs = []

            for i in range(1, 5):
                emb = nextcord.Embed(title=f"Варианты цветов")
                emb.color = nextcord.Colour.random()
                emb.set_image(
                    url=f"https://raw.githubusercontent.com/I-dan-mi-I/images/main/color/{i}.png"
                )
                embs.append(emb)

            try:
                await ctx.message.delete()
                pass
            except nextcord.errors.Forbidden:
                pass

            message = await ctx.send(embed=embs[0], delete_after=60)

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

        else:
            if len(args) < 3:
                await ctx.send(
                    f"{ctx.author.mention}, укажите цвета в формате: <цвет чисел в статистике> <цвет имени> <цвет пунктов статистики>"
                )
            else:
                for e in args:
                    if e not in colors:
                        await ctx.send(
                            f"{ctx.author.mention} такого цвета({e}) нет в списке! Попробуйте снова"
                        )
                        return

                # if not connected to database
                if connected != True:
                    await asyncio.sleep(1)

                if genshin.setColor(
                    self.bot.databaseSession, ctx.guild.id, ctx.author.id, args
                ):
                    await ctx.send(f"{ctx.author.mention} успешно заменено!")
                else:
                    await ctx.send(
                        f"{ctx.author.mention} вашего UID нет в базе! добавить UID"
                    )

    @commands.command(pass_context=True, brief="Выбор фона для статистики и витрины")
    @commands.guild_only()
    async def геншин_фон(self, ctx, *фон):
        global SpreadSheet
        global service

        args = фон

        # if user input blank > send colors magazine
        if args == ():

            embs = []

            for i in range(1, 15):
                emb = nextcord.Embed(title=f"Варианты фонов")
                emb.color = nextcord.Colour.random()
                emb.set_image(
                    url=f"https://raw.githubusercontent.com/I-dan-mi-I/images/main/list/{i}.png"
                )
                embs.append(emb)

            try:
                await ctx.message.delete()
                pass
            except nextcord.errors.Forbidden:
                pass

            message = await ctx.send(embed=embs[0], delete_after=60)

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

        else:
            e = (" ").join(args).lower()
            if e in banners:
                e = f"https://raw.githubusercontent.com/I-dan-mi-I/images/main/banners/{e}.png"

                # if not connected to database
                if connected != True:
                    await asyncio.sleep(1)

                if genshin.setBackground(
                    self.bot.databaseSession, ctx.guild.id, ctx.author.id, e
                ):
                    await ctx.send(f"{ctx.author.mention} успешно заменено!")
                else:
                    await ctx.send(
                        f"{ctx.author.mention} вашего UID нет в базе! добавить UID"
                    )
            else:
                await ctx.send(
                    f"{ctx.author.mention} такого баннера нет в списке! Попробуйте снова"
                )

    @commands.command(
        pass_context=True, brief="Добавить свой HoYoLab ID в базу данных сервера"
    )
    @commands.guild_only()
    async def геншин_добавить(self, ctx, *, hoyolab_id=None):

        hoyolab_id
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

        # if not connected to database

        try:
            card = gs.get_record_card(int(e))
            pass
        except:
            await ctx.send(f"{ctx.author.mention}, ваш HoYoLab ID неверен.")

        try:
            ar = card["level"]
            pass
        except:
            await ctx.send(
                f"{ctx.author.mention}, проверьте настройки приватности и/или привяжите genshin аккаунт"
            )

        uid = card["game_role_id"]
        nickname = card["nickname"]

        emb = nextcord.Embed(
            title=f"{ctx.author.display_name}, проверьте введённые данные"
        )
        emb.add_field(name="Ник", value=nickname)

        emb.add_field(name="Ранг приключений", value=ar)

        emb.add_field(name="UID", value=uid, inline=False)

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

            genshin.addInfo(
                self.bot.databaseSession,
                ctx.guild.id,
                ctx.author.id,
                int(e),
                uid,
                nickname,
                ctx.author.display_name,
                ar,
            )
            emb.title = "Успешно добавлено"
            emb.color = nextcord.Colour.brand_green()
            await msg.edit(embed=emb, view=None)
        else:
            emb.title = "Отменено"
            emb.color = nextcord.Colour.red()
            await msg.edit(embed=emb, view=None)


def setup(bot):
    bot.add_cog(Genshins(bot))
