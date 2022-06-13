import nextcord
from nextcord.ext import commands
from nextcord.ext.commands import Context
from typing import Union
from random import randint
from faker import Faker
import requests
from random import choice
from .phrases import *


class RP(commands.Cog, name="RolePlay"):
    """RolePlay команды"""

    COG_EMOJI: str = "🎭"

    def __init__(self, bot):
        self.bot = bot

    def cog_check(self, ctx: Context) -> bool:
        return ctx.message.guild.id != 876474448126050394

    @commands.command(brief="Проверка совместимости")
    @commands.guild_only()
    async def совместимость(
        self, ctx: Context, пользователь: Union[nextcord.Member, str] = ""
    ):

        if isinstance(пользователь, nextcord.Member):
            embed: nextcord.Embed = nextcord.Embed(
                title=f"{ctx.author.display_name} совместим с {пользователь.display_name} на {randint(0, 100)}%.",
                colour=nextcord.Colour.random(),
            )
        else:
            embed: nextcord.Embed = nextcord.Embed(
                title=f"{ctx.author.display_name} совместим с собой на 100%. Любите себя, это так важно!",
                colour=nextcord.Colour.random(),
            )

        return await ctx.send(embed=embed)

    @commands.command(brief="Шуточное разоблачение пользователя")
    @commands.guild_only()
    async def разоблачение(
        self, ctx: Context, пользователь: Union[nextcord.Member, str] = ""
    ):

        if isinstance(пользователь, nextcord.Member):
            user: nextcord.User = пользователь
        else:
            user: nextcord.User = ctx.author

        await ctx.send(
            f"*Все данные случайны, а совпадения с реальностью непреднамеренные.*\n{user.mention} заранее извиняемся за доставленные неудобства"
        )

        faker = Faker("ru-RU")

        emb: nextcord.Embed = nextcord.Embed(
            title=f"Разоблачение пользователя *__{user.display_name}__*"
        )

        if randint(0, 1):
            emb.add_field(name="ФИО", value=faker.name_male(), inline=True)
        else:
            emb.add_field(name="ФИО", value=faker.name_female(), inline=True)

        emb.add_field(name="Дата рождения", value=faker.date_of_birth(), inline=True)
        emb.add_field(name="Место проживания", value=faker.address(), inline=False)
        emb.add_field(name="Профессия", value=faker.job(), inline=False)
        await ctx.send(embed=emb)

    @commands.command(brief="Обнять пользователя")
    @commands.guild_only()
    async def обнять(
        self, ctx: Context, пользователь: Union[nextcord.Member, str] = ""
    ):

        if isinstance(пользователь, nextcord.Member):
            ans: str = f"{ctx.author.display_name} обнимает {пользователь.display_name}. {choice(ship)}"
        else:
            ans: str = f"{ctx.author.display_name} обнимает сам себя. Любите себя, это так важно! :heart:"

        r: requests.Response = requests.get("https://purrbot.site/api/img/sfw/hug/gif")

        emb: nextcord.Embed = nextcord.Embed(title=ans)
        emb.set_image(url=r.json()["link"])
        emb.colour = nextcord.Colour.random()
        await ctx.send(embed=emb)

    @commands.command(brief="Улыбнуться")
    @commands.guild_only()
    async def улыбнуться(self, ctx: Context):

        emb: nextcord.Embed = nextcord.Embed(
            title=f"{ctx.author.display_name} улыбается. {choice(smile)}"
        )

        r: requests.Response = requests.get(
            "https://purrbot.site/api/img/sfw/smile/gif"
        )

        emb.set_image(url=r.json()["link"])
        emb.colour = nextcord.Colour.random()
        await ctx.send(embed=emb)

    @commands.command(brief="Тыкнуть пользователя")
    @commands.guild_only()
    async def тык(self, ctx: Context, пользователь: Union[nextcord.Member, str] = ""):

        if isinstance(пользователь, nextcord.Member):
            ans: str = f"{ctx.author.display_name} тыкает {ctx.message.mentions[0].display_name}. {choice(poke)}"
        else:
            ans: str = f"{ctx.author.display_name} тыкает сам себя."

        r: requests.Response = requests.get("https://purrbot.site/api/img/sfw/poke/gif")

        emb: nextcord.Embed = nextcord.Embed(title=ans)
        emb.set_image(url=r.json()["link"])
        emb.colour = nextcord.Colour.random()
        await ctx.send(embed=emb)

    @commands.command(brief="Дать пощёчину пользователю")
    @commands.guild_only()
    async def пощёчина(
        self, ctx: Context, пользователь: Union[nextcord.Member, str] = ""
    ):

        if isinstance(пользователь, nextcord.Member):
            ans: str = f"{ctx.author.display_name} даёт пощёчину {ctx.message.mentions[0].display_name}. {choice(slap)}"
        else:
            ans: str = f"{ctx.author.display_name} даёт пощёчину самому себе."

        r: requests.Response = requests.get("https://purrbot.site/api/img/sfw/slap/gif")

        emb: nextcord.Embed = nextcord.Embed(title=ans)
        emb.set_image(url=r.json()["link"])

        emb.colour = nextcord.Colour.random()
        await ctx.send(embed=emb)

    @commands.command(brief="Ударить пользователю")
    @commands.guild_only()
    async def ударить(
        self, ctx: Context, пользователь: Union[nextcord.Member, str] = ""
    ):

        if isinstance(пользователь, nextcord.Member):
            ans: str = f"{ctx.author.display_name} даёт пощёчину {ctx.message.mentions[0].display_name}. {choice(bite)}"
        else:
            ans: str = f"{ctx.author.display_name} бъёт сам себя."

        r: requests.Response = requests.get("https://purrbot.site/api/img/sfw/bite/gif")

        emb: nextcord.Embed = nextcord.Embed(title=ans)
        emb.set_image(url=r.json()["link"])
        emb.colour = nextcord.Colour.random()
        await ctx.send(embed=emb)

    @commands.command(brief="Заплакать")
    @commands.guild_only()
    async def заплакать(self, ctx: Context):

        emb: nextcord.Embed = nextcord.Embed(title=f"{ctx.author.display_name} плачет.")

        r: requests.Response = requests.get("https://purrbot.site/api/img/sfw/cry/gif")

        emb.set_image(url=r.json()["link"])
        emb.colour = nextcord.Colour.random()
        await ctx.send(embed=emb)

    @commands.command(brief="Покраснеть")
    @commands.guild_only()
    async def покраснеть(self, ctx):

        emb: nextcord.Embed = nextcord.Embed(
            title=f"{ctx.author.display_name} краснеет."
        )

        r: requests.Response = requests.get(
            "https://purrbot.site/api/img/sfw/blush/gif"
        )

        emb.set_image(url=r.json()["link"])
        emb.colour = nextcord.Colour.random()
        await ctx.send(embed=emb)

    @commands.command(brief="Поцеловать пользователя")
    @commands.guild_only()
    async def поцеловать(
        self, ctx: Context, пользователь: Union[nextcord.Member, str] = ""
    ):

        if isinstance(пользователь, nextcord.Member):
            ans: str = f"{ctx.author.display_name} целует {ctx.message.mentions[0].display_name}. {choice(ship)}"
        else:
            ans: str = f"{ctx.author.display_name} целует сам себя. Любите себя, это так важно! :heart:"

        r: requests.Response = requests.get("https://purrbot.site/api/img/sfw/kiss/gif")

        emb: nextcord.Embed = nextcord.Embed(title=ans)
        emb.set_image(url=r.json()["link"])
        emb.colour = nextcord.Colour.random()
        await ctx.send(embed=emb)

    @commands.command(brief="Лизнуть пользователя")
    @commands.guild_only()
    async def лизнуть(
        self, ctx: Context, пользователь: Union[nextcord.Member, str] = ""
    ):

        if isinstance(пользователь, nextcord.Member):
            ans: str = f"{ctx.author.display_name} лизает {ctx.message.mentions[0].display_name}. {choice(ship)}"
        else:
            ans: str = f"{ctx.author.display_name} лизает сам себя. Любите себя, это так важно! :heart:"

        r: requests.Response = requests.get("https://purrbot.site/api/img/sfw/lick/gif")

        emb: nextcord.Embed = nextcord.Embed(title=ans)
        emb.set_image(url=r.json()["link"])
        emb.colour: requests.Response = nextcord.Colour.random()
        await ctx.send(embed=emb)

    @commands.command(brief="Погладить пользователя")
    @commands.guild_only()
    async def погладить(
        self, ctx: Context, пользователь: Union[nextcord.Member, str] = ""
    ):

        if isinstance(пользователь, nextcord.Member):
            ans: str = f"{ctx.author.display_name} гладит {ctx.message.mentions[0].display_name}. {choice(ship)}"
        else:
            ans: str = f"{ctx.author.display_name} гладит сам себя. Любите себя, это так важно! :heart:"

        r: requests.Response = requests.get("https://purrbot.site/api/img/sfw/pat/gif")

        emb: nextcord.Embed = nextcord.Embed(title=ans)
        emb.set_image(url=r.json()["link"])
        emb.colour = nextcord.Colour.random()
        await ctx.send(embed=emb)


def setup(bot):
    bot.add_cog(RP(bot))
