# for discord
import nextcord
from nextcord.ext import commands
from settings import settings
from nextcord.ext import tasks
from nextcord.utils import get

# for random
from random import randint

import requests
from io import BytesIO

# for logs
import asyncio
from time import time
from datetime import datetime

# for work with spreadsheet
from database.art import getArt, gcAuthorize

Init = False
gc = None

# first init of spreadsheet
# need google api json
def InitBot():
    global Init
    global gc

    if not Init:
        gc = gcAuthorize()
        print(f"{datetime.now()}|Successful init.")
        Init = 1


class Arts(commands.Cog, name="Арты"):
    """Арты, отобранные специально для вас администрацией нашего сервера."""

    def __init__(self, bot):
        self.bot = bot

    COG_EMOJI = "🖼"

    @commands.command(
        pass_context=True,
        aliases=[f"waifu"],
        brief="Случайная вайфу",
        description="Вайфу, сгенерированная нейросетью",
    )
    @commands.guild_only()
    async def вайфу(self, ctx):
        await ctx.send(
            f"https://www.thiswaifudoesnotexist.net/v2/example-{randint(0, 199999)}.jpg"
        )

    @commands.command(
        pass_context=True,
        brief="Изображение из текста",
        description="Нейросеть генерирует изображение из текста",
    )
    @commands.guild_only()
    async def txt2img(self, ctx, *, текст):

        r = requests.post(
            "https://api.deepai.org/api/text2img",
            data={
                "text": текст,
            },
            headers={"api-key": "6f32333b-6ae8-4222-9b15-a80e6bc0505b"},
        )
        await ctx.send(r.json()["output_url"])

    @commands.command(
        pass_context=True,
        aliases=["friend"],
        brief="Случайный человек",
        description="Нейросеть генерирует фотографию человека",
    )
    @commands.guild_only()
    async def друг(self, ctx):
        im = requests.get("https://thispersondoesnotexist.com/image")
        File = nextcord.File(fp=BytesIO(im.content), filename="friend.jpg")
        await ctx.send(file=File)

    @commands.command(
        pass_content=True, aliases=[f"art"], brief="Арт", description="Арт из таблицы"
    )
    @commands.guild_only()
    async def арт(self, ctx, *, таблица=None):
        global session
        global gc

        args = таблица
        # links to images are taken from the Google spreadsheet sheet, the name of which was specified by the user
        if args is None:
            await ctx.send(f"{ctx.message.author.mention}, укажите имя таблицы")
        else:
            try:
                await ctx.message.delete()
                pass
            except nextcord.errors.Forbidden:
                pass

            InitBot()

            picture = SheetsApi.getPictures(SpreadSheetId, args, SheetService)
            await ctx.send(picture)


def setup(bot):
    bot.add_cog(Arts(bot))
