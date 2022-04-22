# for discord
import nextcord
from nextcord.ext import commands, tasks
from settings import settings
from nextcord.utils import get

# for random
from random import randint

# for logs
import asyncio
from time import time
from datetime import datetime

# for card
from card.rp import *

# для разоблачения
from faker import Faker

# для gif
import requests
import Estrapy
from random import choice

ship = [
    "Шип, шип, шип. Вы не вместе разве?",
    "Шип, шип, шип. Смотритесь так классно!",
    "Теперь мы ждём ваши потрахушки. <3",
    "Я бы не отказался от тройничка с вами \*потирает ручки*",
    "Жру стекло.",
    "Шиппер хочет большего",
]

smile = [
    "Поздравляю, мы только что увидели совершенство!",
    "Слишком идеально, Гугл",
    "Окей, Гугл, где найти идеал?",
]

poke = ["А тыколка не отвалится?", "Ну ладно...", "Он умер в конце"]

slap = [
    "Опупел",
    "Семпай, прекрати",
    "Больше его никто не видел",
    "Вжух💫 И нет половины лица",
]

bite = [
    "СеМпААААй...",
    "Беги...",
    "Тiкай с городу",
    "Он был из тех, кто просто любит жить",
]


class RP(commands.Cog, name="RolePlay"):
    """RolePlay команды"""

    COG_EMOJI = "🎭"

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, brief="Проверка совместимости")
    @commands.guild_only()
    @commands.is_owner()
    async def совместимость_owner(self, ctx, пользователь1=None, пользователь2=None, процент=None):

        if ctx.message.mentions != []:
            user1 = ctx.message.mentions[0]
            user2 = ctx.message.mentions[1]
            if процент is not None:
                compt = процент
            else:
                compt = randint(0, 100)
        else:
            return

        love_card = love_compatibility()
        if user1.avatar is not None:
            love_card.avatar1 = user1.avatar.url
        else:
            love_card.avatar1 = f"https://cdn.discordapp.com/embed/avatars/{str(int(user1.discriminator) % 5)}.png"

        if user2.avatar is not None:
            love_card.avatar2 = user2.avatar.url
        else:
            love_card.avatar2 = f"https://cdn.discordapp.com/embed/avatars/{str(int(user2.discriminator) % 5)}.png"

        love_card.comp = int(compt)

        # sending image to discord channel
        await ctx.send(file=await love_card.create())

    @commands.command(pass_context=True, brief="Проверка совместимости")
    @commands.guild_only()
    async def совместимость(self, ctx, *пользователь):

        usr = пользователь
        if ctx.message.mentions != []:
            user = ctx.message.mentions[0]
            compt = randint(0, 100)
        else:
            # check user input
            if usr == ():
                user = ctx.author
                compt = 100
            else:
                usr = usr[0]

                try:
                    user = await ctx.guild.fetch_member(usr)
                    compt = randint(0, 100)
                    pass
                except Exception as el:
                    print(el)
                    user = ctx.author
                    compt = 100
                    pass

        love_card = love_compatibility()
        if ctx.author.avatar is not None:
            love_card.avatar1 = ctx.author.avatar.url
        else:
            love_card.avatar1 = f"https://cdn.discordapp.com/embed/avatars/{str(int(ctx.author.discriminator)%5)}.png"

        if user.avatar is not None:
            love_card.avatar2 = user.avatar.url
        else:
            love_card.avatar2 = f"https://cdn.discordapp.com/embed/avatars/{str(int(user.discriminator)%5)}.png"

        love_card.comp = compt

        # sending image to discord channel
        await ctx.send(file=await love_card.create())

    @commands.command(pass_context=True, brief="Шуточное разоблачение пользователя")
    @commands.guild_only()
    async def разоблачение(self, ctx, *пользователь):

        usr = пользователь
        if usr == ():
            user = ctx.author
        else:
            try:
                user = ctx.message.mentions[0]
            except:
                await ctx.send("Неверный ввод!")
                return

        await ctx.send(
            f"*Все данные случайны, а совпадения с реальностью непреднамеренные.*\n{user.mention} заранее извиняемся за доставленные неудобства"
        )

        faker = Faker("ru-RU")

        emb = nextcord.Embed(
            title=f"Разоблачение пользователя *__{user.display_name}__*"
        )

        if (
            str(user.roles).find("I am boy") != -1
            or str(user.roles).find("Участники клуба") != -1
        ):
            emb.add_field(name="ФИО", value=faker.name_male(), inline=True)
        else:
            emb.add_field(name="ФИО", value=faker.name_female(), inline=True)
        emb.add_field(name="Дата рождения", value=faker.date_of_birth(), inline=True)
        emb.add_field(name="Место проживания", value=faker.address(), inline=False)
        emb.add_field(name="Профессия", value=faker.job(), inline=False)
        await ctx.send(embed=emb)

    @commands.command(pass_context=True, brief="Обнять пользователя")
    @commands.guild_only()
    async def обнять(self, ctx, пользователь=None):

        if пользователь is None:
            ans = f"{ctx.author.display_name} обнимает сам себя. Любите себя, это так важно! :heart:"
        else:
            try:
                ans = f"{ctx.author.display_name} обнимает {ctx.message.mentions[0].display_name}. {choice(ship)}"
            except:
                ans = f"{ctx.author.display_name} обнимает сам себя. Любите себя, это так важно! :heart:"
                pass

        r = requests.get("https://purrbot.site/api/img/sfw/hug/gif")

        emb = nextcord.Embed(title=ans)
        emb.set_image(url=r.json()["link"])
        emb.color = nextcord.Colour.random()
        await ctx.send(embed=emb)

    @commands.command(pass_context=True, brief="Улыбнуться")
    @commands.guild_only()
    async def улыбнуться(self, ctx):

        emb = nextcord.Embed(
            title=f"{ctx.author.display_name} улыбается. {choice(smile)}"
        )

        r = requests.get("https://purrbot.site/api/img/sfw/smile/gif")

        emb.set_image(url=r.json()["link"])
        emb.color = nextcord.Colour.random()
        await ctx.send(embed=emb)

    @commands.command(pass_context=True, brief="Тыкнуть пользователя")
    @commands.guild_only()
    async def тык(self, ctx, пользователь=None):

        if пользователь is None:
            ans = f"{ctx.author.display_name} тыкает сам себя."
        else:
            try:
                ans = f"{ctx.author.display_name} тыкает {ctx.message.mentions[0].display_name}. {choice(poke)}"
            except:
                ans = f"{ctx.author.display_name} тыкает сам себя."
                pass

        r = requests.get("https://purrbot.site/api/img/sfw/poke/gif")

        emb = nextcord.Embed(title=ans)
        emb.set_image(url=r.json()["link"])
        emb.color = nextcord.Colour.random()
        await ctx.send(embed=emb)

    @commands.command(pass_context=True, brief="Дать пощёчину пользователю")
    @commands.guild_only()
    async def пощёчина(self, ctx, пользователь=None):

        if пользователь is None:
            ans = f"{ctx.author.display_name} даёт пощёчину самому себе."
        else:
            try:
                ans = f"{ctx.author.display_name} даёт пощёчину {ctx.message.mentions[0].display_name}. {choice(slap)}"
            except:
                ans = f"{ctx.author.display_name} даёт пощёчину самому себе."
                pass

        r = requests.get("https://purrbot.site/api/img/sfw/slap/gif")

        emb = nextcord.Embed(title=ans)
        emb.set_image(url=r.json()["link"])

        emb.color = nextcord.Colour.random()
        await ctx.send(embed=emb)

    @commands.command(pass_context=True, brief="Ударить пользователю")
    @commands.guild_only()
    async def ударить(self, ctx, пользователь=None):

        if пользователь is None:
            ans = f"{ctx.author.display_name} бьёт сам себя."
        else:
            try:
                ans = f"{ctx.author.display_name} даёт пощёчину {ctx.message.mentions[0].display_name}. {choice(bite)}"
            except:
                ans = f"{ctx.author.display_name} бъёт сам себя."
                pass

        r = requests.get("https://purrbot.site/api/img/sfw/bite/gif")

        emb = nextcord.Embed(title=ans)
        emb.set_image(url=r.json()["link"])
        emb.color = nextcord.Colour.random()
        await ctx.send(embed=emb)

    @commands.command(pass_context=True, brief="Дать пять пользователю")
    @commands.guild_only()
    async def дать_пять(self, ctx, пользователь=None):

        if пользователь is None:
            ans = f"{ctx.author.display_name} даёт пять самому себе."
        else:
            try:
                ans = f"{ctx.author.display_name} даёт пять {ctx.message.mentions[0].display_name}."
            except:
                ans = f"{ctx.author.display_name} даёт пять самому себе."
                pass

        emb = nextcord.Embed(title=ans)
        emb.set_image(url=await Estrapy.Sfw.highfive())
        emb.color = nextcord.Colour.random()
        await ctx.send(embed=emb)

    @commands.command(pass_context=True, brief="Заплакать")
    @commands.guild_only()
    async def заплакать(self, ctx):

        emb = nextcord.Embed(title=f"{ctx.author.display_name} плачет.")

        r = requests.get("https://purrbot.site/api/img/sfw/cry/gif")

        emb.set_image(url=r.json()["link"])
        emb.color = nextcord.Colour.random()
        await ctx.send(embed=emb)

    @commands.command(pass_context=True, brief="Покраснеть")
    @commands.guild_only()
    async def покраснеть(self, ctx):

        emb = nextcord.Embed(title=f"{ctx.author.display_name} краснеет.")

        r = requests.get("https://purrbot.site/api/img/sfw/blush/gif")

        emb.set_image(url=r.json()["link"])
        emb.color = nextcord.Colour.random()
        await ctx.send(embed=emb)

    @commands.command(pass_context=True, brief="Поцеловать пользователя")
    @commands.guild_only()
    async def поцеловать(self, ctx, пользователь=None):

        if пользователь is None:
            ans = f"{ctx.author.display_name} целует сам себя. Любите себя, это так важно! :heart:"
        else:
            try:
                ans = f"{ctx.author.display_name} целует {ctx.message.mentions[0].display_name}. {choice(ship)}"
            except:
                ans = f"{ctx.author.display_name} целует сам себя. Любите себя, это так важно! :heart:"
                pass

        r = requests.get("https://purrbot.site/api/img/sfw/kiss/gif")

        emb = nextcord.Embed(title=ans)
        emb.set_image(url=r.json()["link"])
        emb.color = nextcord.Colour.random()
        await ctx.send(embed=emb)

    @commands.command(pass_context=True, brief="Лизнуть пользователя")
    @commands.guild_only()
    async def лизнуть(self, ctx, пользователь=None):

        if пользователь is None:
            ans = f"{ctx.author.display_name} лизает сам себя. Любите себя, это так важно! :heart:"
        else:
            try:
                ans = f"{ctx.author.display_name} лизает {ctx.message.mentions[0].display_name}. {choice(ship)}"
            except:
                ans = f"{ctx.author.display_name} лизает сам себя. Любите себя, это так важно! :heart:"
                pass

        r = requests.get("https://purrbot.site/api/img/sfw/lick/gif")

        emb = nextcord.Embed(title=ans)
        emb.set_image(url=r.json()["link"])
        emb.color = nextcord.Colour.random()
        await ctx.send(embed=emb)

    @commands.command(pass_context=True, brief="Погладить пользователя")
    @commands.guild_only()
    async def погладить(self, ctx, пользователь=None):

        if пользователь is None:
            ans = f"{ctx.author.display_name} гладит сам себя. Любите себя, это так важно! :heart:"
        else:
            try:
                ans = f"{ctx.author.display_name} гладит {ctx.message.mentions[0].display_name}. {choice(ship)}"
            except:
                ans = f"{ctx.author.display_name} гладит сам себя. Любите себя, это так важно! :heart:"
                pass

        r = requests.get("https://purrbot.site/api/img/sfw/pat/gif")

        emb = nextcord.Embed(title=ans)
        emb.set_image(url=r.json()["link"])
        emb.color = nextcord.Colour.random()
        await ctx.send(embed=emb)


def setup(bot):
    bot.add_cog(RP(bot))
