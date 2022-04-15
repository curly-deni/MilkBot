# for discord
import nextcord
from nextcord.ext import commands, tasks
from settings import settings
from nextcord.utils import get

# for logs
import asyncio
from time import time
from datetime import datetime

# для gif
import requests


class RP_NSFW(commands.Cog, name="RolePlay [NSFW]"):
    """RolePlay 18+ команды"""

    COG_EMOJI = "🔞"

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.errors.NSFWChannelRequired):
            emb = nextcord.Embed(
                title="Команда предназначена для NSFW-чата", description=error.args[0]
            )
            return await ctx.send(embed=emb, delete_after=15)

    @commands.command(pass_context=True, brief="Заняться сексом пользователя")
    @commands.is_nsfw()
    @commands.guild_only()
    async def секс(self, ctx, пользователь=None):

        if пользователь is None:
            ans = f"{ctx.author.display_name} занимается сексом сам с собой. Любите себя, это так важно! :heart:"
        else:
            try:
                ans = f"{ctx.author.display_name} занимается сексом с {ctx.message.mentions[0].display_name}."
            except:
                ans = f"{ctx.author.display_name} занимается сексом сам с собой. Любите себя, это так важно! :heart:"
                pass

        r = requests.get("https://purrbot.site/api/img/nsfw/fuck/gif")

        emb = nextcord.Embed(title=ans)
        emb.set_image(url=r.json()["link"])
        emb.color = nextcord.Colour.random()
        await ctx.send(embed=emb)

    """@commands.command(pass_context=True, brief="Улыбнуться")
    @commands.is_nsfw()
    @commands.guild_only()
    async def улыбнуться_nsfw(self, ctx):

        emb = nextcord.Embed(
            title=f"{ctx.author.display_name} улыбается. {choice(smile)}"
        )

        r = requests.get(
            "https://purrbot.site/api/img/sfw/smile/gif"
        )

        emb.set_image(url=r.json()["link"])
        emb.color = nextcord.Colour.random()
        await ctx.send(embed=emb)"""


def setup(bot):
    bot.add_cog(RP_NSFW(bot))
