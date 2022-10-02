import nextcord
from nextcord.ext import commands
from nextcord.ext.commands import Context
from typing import Optional
from random import randint
from faker import Faker
import requests
from random import choice
from .phrases import *
from .pictures import *
from datetime import datetime


def not_seals_check(ctx: Context) -> bool:
    return ctx.message.guild.id != 876474448126050394


def seals_check(ctx: Context) -> bool:
    return ctx.message.guild.id == 876474448126050394


class RP(commands.Cog, name="RolePlay"):
    """RolePlay команды"""

    COG_EMOJI: str = "🎭"

    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Обнять пользователя", aliases=["cuddle", "hug"])
    @commands.guild_only()
    async def обнять(self, ctx: Context):

        embed: nextcord.Embed = nextcord.Embed(
            title=f"{ctx.author.display_name} обнимает ",
            colour=nextcord.Colour.random(),
            timestamp=datetime.now(),
        )

        if not ctx.message.mentions:
            embed.title += f"сам себя. {alone}"
        else:
            embed.title += (
                ", ".join(member.display_name for member in ctx.message.mentions)
                + f". {choice(ship_phrases)}"
            )

        if seals_check(ctx) and randint(0, 1) == 0:
            embed.set_image(url=choice(hug))
            embed.set_footer(text='GIF предоставлен базой данных бота "Кисик"')
        else:
            r: requests.Response = requests.get(
                "https://purrbot.site/api/img/sfw/hug/gif"
            )
            embed.set_image(url=r.json()["link"])
            embed.set_footer(text='GIF предоставлен базой данных бота "PurrBot"')

        await ctx.send(embed=embed)

    @commands.command(brief="Улыбнуться", aliases=["smile"])
    @commands.guild_only()
    async def улыбнуться(self, ctx: Context):

        emb: nextcord.Embed = nextcord.Embed(
            title=f"{ctx.author.display_name} улыбается. {choice(smile_phrases)}"
        )

        r: requests.Response = requests.get(
            "https://purrbot.site/api/img/sfw/smile/gif"
        )

        emb.set_footer(text='GIF предоставлен базой данных бота "PurrBot"')

        emb.set_image(url=r.json()["link"])
        emb.colour = nextcord.Colour.random()
        await ctx.send(embed=emb)

    @commands.command(brief="Тыкнуть пользователя", aliases=["poke"])
    @commands.guild_only()
    async def тык(self, ctx: Context):

        embed: nextcord.Embed = nextcord.Embed(
            title=f"{ctx.author.display_name} тыкает ",
            colour=nextcord.Colour.random(),
            timestamp=datetime.now(),
        )

        if not ctx.message.mentions:
            embed.title += "сам себя."
        else:
            embed.title += (
                ", ".join(member.display_name for member in ctx.message.mentions)
                + f". {choice(poke_phrases)}"
            )

        embed.set_footer(text='GIF предоставлен базой данных бота "PurrBot"')

        r: requests.Response = requests.get("https://purrbot.site/api/img/sfw/poke/gif")
        embed.set_image(url=r.json()["link"])
        await ctx.send(embed=embed)

    @commands.command(brief="Дать пощёчину пользователю", aliases=["slap"])
    @commands.guild_only()
    async def пощёчина(self, ctx: Context):
        embed: nextcord.Embed = nextcord.Embed(
            title=f"{ctx.author.display_name} даёт пощёчину ",
            colour=nextcord.Colour.random(),
            timestamp=datetime.now(),
        )

        if not ctx.message.mentions:
            embed.title += f"самому себе. {alone}"
        else:
            embed.title += (
                ", ".join(member.display_name for member in ctx.message.mentions)
                + f". {choice(slap_phrases)}"
            )

        if seals_check(ctx) and randint(0, 1) == 0:
            embed.set_image(url=choice(slap))
            embed.set_footer(text='GIF предоставлен базой данных бота "Кисик"')
        else:
            r: requests.Response = requests.get(
                "https://purrbot.site/api/img/sfw/slap/gif"
            )
            embed.set_image(url=r.json()["link"])
            embed.set_footer(text='GIF предоставлен базой данных бота "PurrBot"')

        await ctx.send(embed=embed)

    @commands.command(brief="Ударить пользователю", aliases=["bite"])
    @commands.guild_only()
    async def ударить(self, ctx: Context):

        embed: nextcord.Embed = nextcord.Embed(
            title=f"{ctx.author.display_name} ударяет ",
            colour=nextcord.Colour.random(),
            timestamp=datetime.now(),
        )

        if not ctx.message.mentions:
            embed.title += f"сам себя. {alone}"
        else:
            embed.title += (
                ", ".join(member.display_name for member in ctx.message.mentions)
                + f". {choice(bite_phrases)}"
            )

        if seals_check(ctx) and randint(0, 1) == 0:
            embed.set_image(url=choice(bite))
            embed.set_footer(text='GIF предоставлен базой данных бота "Кисик"')
        else:
            r: requests.Response = requests.get(
                "https://purrbot.site/api/img/sfw/bite/gif"
            )
            embed.set_image(url=r.json()["link"])
            embed.set_footer(text='GIF предоставлен базой данных бота "PurrBot"')

        await ctx.send(embed=embed)

    @commands.command(brief="Заплакать", aliases=["cry"])
    @commands.guild_only()
    async def заплакать(self, ctx: Context):

        emb: nextcord.Embed = nextcord.Embed(title=f"{ctx.author.display_name} плачет.")

        emb.set_footer(text='GIF предоставлен базой данных бота "PurrBot"')

        r: requests.Response = requests.get("https://purrbot.site/api/img/sfw/cry/gif")

        emb.set_image(url=r.json()["link"])
        emb.colour = nextcord.Colour.random()
        await ctx.send(embed=emb)

    @commands.command(brief="Покраснеть", aliases=["blush"])
    @commands.guild_only()
    async def покраснеть(self, ctx):

        emb: nextcord.Embed = nextcord.Embed(
            title=f"{ctx.author.display_name} краснеет."
        )

        r: requests.Response = requests.get(
            "https://purrbot.site/api/img/sfw/blush/gif"
        )

        emb.set_footer(text='GIF предоставлен базой данных бота "PurrBot"')

        emb.set_image(url=r.json()["link"])
        emb.colour = nextcord.Colour.random()
        await ctx.send(embed=emb)

    @commands.command(brief="Поцеловать пользователя", aliases=["kiss"])
    @commands.guild_only()
    async def поцеловать(self, ctx: Context):

        embed: nextcord.Embed = nextcord.Embed(
            title=f"{ctx.author.display_name} целует ",
            colour=nextcord.Colour.random(),
            timestamp=datetime.now(),
        )

        if not ctx.message.mentions:
            embed.title += f"сам себя. {alone}"
        else:
            embed.title += (
                ", ".join(member.display_name for member in ctx.message.mentions)
                + f". {choice(ship_phrases)}"
            )

        if seals_check(ctx) and randint(0, 1) == 0:
            embed.set_image(url=choice(kiss))
            embed.set_footer(text='GIF предоставлен базой данных бота "Кисик"')
        else:
            r: requests.Response = requests.get(
                "https://purrbot.site/api/img/sfw/kiss/gif"
            )
            embed.set_image(url=r.json()["link"])
            embed.set_footer(text='GIF предоставлен базой данных бота "PurrBot"')

        await ctx.send(embed=embed)

    @commands.command(brief="Лизнуть пользователя", aliases=["lick"])
    @commands.guild_only()
    async def лизнуть(self, ctx: Context):
        embed: nextcord.Embed = nextcord.Embed(
            title=f"{ctx.author.display_name} облизывает ",
            colour=nextcord.Colour.random(),
            timestamp=datetime.now(),
        )

        if not ctx.message.mentions:
            embed.title += f"сам себя. {alone}"
        else:
            embed.title += (
                ", ".join(member.display_name for member in ctx.message.mentions)
                + f". {choice(ship_phrases)}"
            )

        if seals_check(ctx) and randint(0, 1) == 0:
            embed.set_image(url=choice(lick))
            embed.set_footer(text='GIF предоставлен базой данных бота "Кисик"')
        else:
            r: requests.Response = requests.get(
                "https://purrbot.site/api/img/sfw/lick/gif"
            )
            embed.set_image(url=r.json()["link"])
            embed.set_footer(text='GIF предоставлен базой данных бота "PurrBot"')

        await ctx.send(embed=embed)

    @commands.command(brief="Погладить пользователя")
    @commands.guild_only()
    async def погладить(self, ctx: Context):

        embed: nextcord.Embed = nextcord.Embed(
            title=f"{ctx.author.display_name} гладит ",
            colour=nextcord.Colour.random(),
            timestamp=datetime.now(),
        )

        if not ctx.message.mentions:
            embed.title += f"сам себя. {alone}"
        else:
            embed.title += (
                ", ".join(member.display_name for member in ctx.message.mentions)
                + f". {choice(ship_phrases)}"
            )

        embed.set_footer(text='GIF предоставлен базой данных бота "PurrBot"')

        r: requests.Response = requests.get("https://purrbot.site/api/img/sfw/pat/gif")
        embed.set_image(url=r.json()["link"])
        await ctx.send(embed=embed)

    @commands.command(
        brief="Спать/уложить спать пользователя (при его упоминании)",
        aliases=["sleep", "уложить_спать"],
    )
    @commands.guild_only()
    async def спать(self, ctx: Context):
        embed: nextcord.Embed = nextcord.Embed(
            colour=nextcord.Colour.random(), timestamp=datetime.now()
        )

        if not ctx.message.mentions:
            embed.title = f"{ctx.author.display_name} спит"
            embed.set_image(url=choice(sleep))
        else:
            embed.title = (
                f"{ctx.author.display_name} укладывает спать "
                + ", ".join(member.display_name for member in ctx.message.mentions)
                + f". {choice(ship_phrases)}"
            )
            embed.set_image(url=choice(sleep_two))

        embed.set_footer(text='GIF предоставлен базой данных бота "Кисик"')

        await ctx.send(embed=embed)

    @commands.command(brief="Покормить пользователя", aliases=["feed"])
    @commands.guild_only()
    async def покормить(self, ctx: Context):
        embed: nextcord.Embed = nextcord.Embed(
            colour=nextcord.Colour.random(), timestamp=datetime.now()
        )

        if not ctx.message.mentions:
            embed.title = f"{ctx.author.display_name} кушает."
        else:
            embed.title += f"{ctx.author.display_name} кормит " + ", ".join(
                member.display_name for member in ctx.message.mentions
            )

        if seals_check(ctx) and randint(0, 1) == 0:
            embed.set_image(url=choice(feed))
            embed.set_footer(text='GIF предоставлен базой данных бота "Кисик"')
        else:
            r: requests.Response = requests.get(
                "https://purrbot.site/api/img/sfw/feed/gif"
            )
            embed.set_image(url=r.json()["link"])
            embed.set_footer(text='GIF предоставлен базой данных бота "PurrBot"')

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(RP(bot))
