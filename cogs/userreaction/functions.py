# for discord
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

# for chance
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


class UserReactions(commands.Cog):
    """Discord.py based class for User Reaction"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):

        # buy in new year

        if message.content.lower().find("мда") != -1:
            if chance(50, message.author.id):
                await message.channel.send("треш")


def setup(bot):
    bot.add_cog(UserReactions(bot))
