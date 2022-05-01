# for discord
import nextcord
from nextcord.ext import commands
from nextcord.utils import get

# data base
import database.stat as stat

# for card
from card.stat import *
import unicodedata

# for multipage embed
from nextcord_paginator import paginator as Paginator

# for cards
from settings import banners  # name of cards
from settings import colors  # name of colors from Pillow

from additional.check_permission import check_admin_permissions


def massive_split(mas):
    masx = []
    l10 = len(mas) // 10
    for i in range(l10 + 1):
        masx.append(mas[i * 10 : (i + 1) * 10])
    return masx


class Stats(commands.Cog, name="Статистика"):
    """Статистика пользователей сервера"""

    COG_EMOJI = "📓"

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, brief="Статистика пользователя")
    @commands.guild_only()
    async def ранг(self, ctx, пользователь):

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
                except:
                    return await ctx.send("Неверный ввод!")

        # if not connected to database

        x = stat.getInfo(self.bot.databaseSession, ctx.guild.id, user.id)

        statcard = newstat()

        if user.avatar is not None:
            statcard.avatar = user.avatar.url
        else:
            statcard.avatar = f"https://cdn.discordapp.com/embed/avatars/{str(int(user.discriminator)%5)}.png"

        statcard.name = unicodedata.normalize("NFKC", str(user.display_name))

        statcard.color = x.color

        statcard.path = x.background

        statcard.coin = x.coin

        statcard.quote = x.quotex

        if x.allvoicetime is None:
            statcard.voicetime = 0
        else:
            statcard.voicetime = x.allvoicetime

        if x.cookie is None:
            statcard.cookie = 0
        else:
            statcard.cookie = x.cookie

        if x.xp is None:
            statcard.xp = 0
        else:
            statcard.xp = x.xp

        if x.lvl is None:
            statcard.lvl = 0
        else:
            statcard.lvl = x.lvl

        # sending image to discord channel
        await ctx.send(file=await statcard.create())

    @commands.command(brief="Топ пользователей сервера")
    @commands.guild_only()
    async def лидеры(self, ctx):

        peoples_undefined = list(
            stat.getAllInfoSorted(self.bot.databaseSession, ctx.guild.id)
        )
        peoples = []

        for people in peoples_undefined:
            member = get(ctx.guild.members, id=people.uid)
            if member is not None:
                if not member.bot:
                    peoples.append([member, people])

        peoples = massive_split(peoples)

        s = 0
        embs = []
        for people_list in peoples:
            emb = nextcord.Embed(title=f"Топ пользователей | {ctx.guild.name}")
            emb.color = nextcord.Colour.green()
            emb.set_thumbnail(url=ctx.guild.icon.url)

            for idx, items in enumerate(people_list):
                if items[1].lvl is not None:
                    strx = f"**Уровень:** {items[1].lvl}|"
                else:
                    strx = f"**Уровень:** 0|"

                if items[1].xp is not None:
                    strx = strx + f"**Опыт:** {items[1].xp}|"
                else:
                    strx = strx + f"**Опыт:** 0|"

                if items[1].cookie is not None:
                    if items[1].cookie != 0:
                        strx = strx + f":cookie: {items[1].cookie}|"

                if items[1].coin is not None:
                    if items[1].coin != 0:
                        strx = strx + f":coin: {items[1].coin}|"

                if items[1].allvoicetime is not None:
                    if items[1].allvoicetime != 0:
                        hours = items[1].allvoicetime // 3600
                        minutes = (items[1].allvoicetime % 3600) // 60
                        if minutes < 10:
                            minutes = "0" + str(minutes)
                        seconds = (items[1].allvoicetime % 3600) % 60
                        if seconds < 10:
                            seconds = "0" + str(seconds)

                        strx = strx + f":microphone: {hours}:{minutes}:{seconds}"

                name = items[0].display_name

                emb.add_field(
                    name=f"{s*10 + idx + 1}. {name}",
                    value=strx,
                    inline=False,
                )

            embs.append(emb)
            s += 1

        try:
            await ctx.message.delete()
        except:
            pass

        message = await ctx.send(embed=embs[0])

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

    @commands.command(pass_context=True, brief="Выбор цвета для статистики")
    @commands.guild_only()
    async def цвет(self, ctx, *цвет):

        global colors

        args = цвет

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

        # else set color to database
        else:
            e = (" ").join(args).lower()
            if e in colors:

                # if not connected to database

                stat.setColor(self.bot.databaseSession, ctx.guild.id, ctx.author.id, e)
                await ctx.send(f"{ctx.author.mention} успешно заменено!")
            else:
                await ctx.send(
                    f"{ctx.author.mention} такого цвета нет в списке! Попробуйте снова"
                )

    @commands.command(pass_context=True, brief="Выбор фона для статистики")
    @commands.guild_only()
    async def фон(self, ctx, *фон):

        global banners

        args = фон

        # if user input blank > send banners magazine
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

        # else set banner to database
        else:
            e = (" ").join(args).lower()
            if e in banners:
                e = f"https://raw.githubusercontent.com/I-dan-mi-I/images/main/cards/{e}.png"

                # if not connected to database

                stat.setBackground(
                    self.bot.databaseSession, ctx.guild.id, ctx.author.id, e
                )
                await ctx.send(f"{ctx.author.mention} успешно заменено!")
            else:
                await ctx.send(
                    f"{ctx.author.mention} такого баннера нет в списке! Попробуйте снова"
                )

    @commands.command(
        pass_context=True,
        aliases=[f"coin"],
        brief="Редактирование количества монет пользователя",
    )
    @commands.check(check_admin_permissions)
    @commands.guild_only()
    async def шар(self, ctx, пользователь, количество):

        if пользователь is None:
            await ctx.send(
                f"{ctx.author.mention}, укажите uid (отметьте пользователя) и кол-во шаров, которые вы ему добавите!"
            )
        else:
            if not пользователь.startswith("<"):
                try:
                    user = await ctx.guild.fetch_member(пользователь)
                except:
                    return await ctx.send("Неверный ввод")
            else:
                try:
                    user = ctx.message.mentions[0]
                except:
                    return await ctx.send("Неверный ввод!")

            try:
                ball = int(количество)
            except:
                return await ctx.send("Неверный ввод числа шаров!")

            stat.addBalls(self.bot.databaseSession, ctx.guild.id, user.id, ball)
            await ctx.send(f"{ctx.author.mention}, добавлено!")

    @commands.command(pass_context=True, brief="Установка цитаты для статистики")
    @commands.guild_only()
    async def цитата(self, ctx, *цитата):

        args = цитата

        if args == ():
            await ctx.send(
                f"{ctx.author.mention}, напишите цитату после команды. Максимальная длина: 33 символа, включая пробелы."
            )
        else:
            e = (" ").join(args)
            if len(e) <= 33:

                stat.setQuote(self.bot.databaseSession, ctx.guild.id, ctx.author.id, e)
                await ctx.send(f"{ctx.author.mention}, успешно заменено!")
            else:
                await ctx.send(
                    f"{ctx.author.mention}, Максимальная длина: 33 символа, включая пробелы! Попробуйте снова"
                )


def setup(bot):
    bot.add_cog(Stats(bot))
