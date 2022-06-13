# for nextcord
import nextcord
from nextcord.ext import commands
from nextcord.ext.commands import Context

import random
from .pictures import *


class KisikRP(commands.Cog, name="[Кисик] RolePlay"):
    """RolePlay команды из Кисика"""

    COG_EMOJI: str = "🎭"

    def __init__(self, bot):
        self.bot = bot

    def cog_check(self, ctx: Context) -> bool:
        return ctx.message.guild.id in [876474448126050394, 938461972448559116]

    @commands.command(brief="Укусить пользователя")
    @commands.guild_only()
    async def bite(self, ctx: Context, user: nextcord.Member = None):
        if not user:
            await ctx.send("Требуется упоминание участника!", delete_after=10)
        else:
            embed = nextcord.Embed(
                description=f"**{ctx.message.author.display_name}** кусает **{user.display_name}**",
                colour=nextcord.Colour.random(),
            )
            embed.set_image(url=random.choice(bite))
            await ctx.send(embed=embed)

    @bite.error
    async def bite_error(self, ctx: Context, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Я не могу найти этого человека.")

    @commands.command(aliases=["food"], brief="Покормить пользователя")
    @commands.guild_only()
    async def feed(self, ctx: Context, user: nextcord.Member = None):
        if not user:
            await ctx.send("Требуется упоминание участника!", delete_after=10)
        else:
            embed = nextcord.Embed(
                description=f"**{ctx.message.author.display_name}** кормит **{user.display_name}**",
                colour=nextcord.Colour.random(),
            )
            embed.set_image(url=random.choice(feed))
            await ctx.send(embed=embed)

    @feed.error
    async def feed_error(self, ctx: Context, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Я не могу найти этого человека.")

    @commands.command(aliases=["love"], brief="Поцеловать пользователя")
    @commands.guild_only()
    async def kiss(self, ctx: Context, user: nextcord.Member = None):
        if not user:
            await ctx.send("Требуется упоминание участника!", delete_after=10)
        else:
            embed = nextcord.Embed(
                description=f"**{ctx.message.author.display_name}** целует **{user.display_name}**",
                colour=nextcord.Colour.random(),
            )
            embed.set_image(url=random.choice(kiss))
            await ctx.send(embed=embed)

    @kiss.error
    async def kiss_error(self, ctx: Context, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Я не могу найти этого человека.")

    @commands.command(brief="Облизать пользователя")
    async def lick(self, ctx: Context, user: nextcord.Member = None):
        if not user:
            await ctx.send("Требуется упоминание участника!", delete_after=10)
        else:
            embed = nextcord.Embed(
                description=f"**{ctx.message.author.display_name}** облизывает **{user.display_name}**",
                colour=nextcord.Colour.random(),
            )
            embed.set_image(url=random.choice(lick))
            await ctx.send(embed=embed)

    @lick.error
    async def lick_error(self, ctx: Context, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Я не могу найти этого человека.", delete_after=10)

    @commands.command(brief="Шлёпнуть пользователя")
    async def slap(self, ctx: Context, user: nextcord.Member = None):
        if not user:
            await ctx.send("Требуется упоминание участника!", delete_after=10)
        else:
            embed = nextcord.Embed(
                description=f"**{ctx.message.author.display_name}** шлёпает **{user.display_name}**",
                colour=nextcord.Colour.random(),
            )
            embed.set_image(url=random.choice(slap))
            await ctx.send(embed=embed)

    @slap.error
    async def slap_error(self, ctx: Context, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Я не могу найти этого человека.", delete_after=10)

    @commands.command(aliases=["cuddle"], brief="Обнять пользователя")
    async def hug(self, ctx: Context, user: nextcord.Member = None):
        if not user:
            await ctx.send("Требуется упоминание участника!", delete_after=10)
        else:
            embed = nextcord.Embed(
                description=f"**{ctx.message.author.display_name}** обнимает **{user.display_name}**",
                colour=nextcord.Colour.random(),
            )
            print(random.choice(hug))
            embed.set_image(url=random.choice(hug))
            await ctx.send(embed=embed)

    @hug.error
    async def hug_error(self, ctx: Context, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Я не могу найти этого человека.")

    @commands.command(brief="Спать/уложить спать пользователя (при его упоминании)")
    async def sleep(self, ctx: Context, user: nextcord.Member = None):
        if user is None:
            embed = nextcord.Embed(
                description=f"**{ctx.message.author.display_name}** спит",
                colour=nextcord.Colour.random(),
            )
            embed.set_image(url=random.choice(sleep))
            await ctx.send(embed=embed)
        else:
            embed = nextcord.Embed(
                description=f"**{ctx.message.author.display_name}** укладывает спать **{user.display_name}**",
                colour=nextcord.Colour.random(),
            )
            embed.set_image(url=random.choice(sleep_two))
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(KisikRP(bot))
