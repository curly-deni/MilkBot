# for nextcord
import nextcord
from nextcord.ext import commands

# for chance
from random import randint
from math import floor
from settings import ignorechance

# for logs
import asyncio
from time import time
from datetime import datetime


def chance(ch, user):
    if user not in ignorechance:
        try:
            c = floor(100 / ch)
            pass
        except:
            return False
        if randint(1, c) == 1:
            return True
    else:
        return True


class IntReactions(commands.Cog):
    """Discord.py based class for Internal Reaction"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):

        # internal reactions

        if (
            message.content.lower().find("программист") != -1
            or message.content.lower().find("погромист") != -1
        ):
            if chance(50, message.author.id):
                await message.channel.send("ууу... питонист-онанист")

        if (
            message.content.lower().find("гонер") != -1
            or message.content.lower().find("жора") != -1
        ):
            if chance(12, message.author.id):
                await message.channel.send("кочка")

        if (
            message.content.lower().find("дима, блять") != -1
            or message.content.lower().find("дима блять") != -1
        ):
            await message.channel.send("<:bottle:571094733452083296>")

        if message.content.lower().find("criminal") != -1:
            await message.channel.send("мама ама криминал")

        if message.content.lower().find("казахстан") != -1:
            await message.channel.send("слава питсе")

        if (
            message.content.lower().find("даня блять") != -1
            or message.content.lower().find("даня, блять") != -1
        ):
            await message.channel.send("ЪуЪ")


def setup(bot):
    bot.add_cog(IntReactions(bot))
