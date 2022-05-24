# for discord
import nextcord
from nextcord.ext import commands
from nextcord.ext.commands import Context

# for random
from random import randint


class Arts(commands.Cog, name="Арты"):
    """Арты, отобранные специально для вас администрацией нашего сервера."""

    def __init__(self, bot):
        self.bot = bot

    COG_EMOJI = "🖼"

    def cog_check(self, ctx: Context) -> bool:
        return ctx.message.guild.id != 876474448126050394

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
        pass_content=True, aliases=[f"art"], brief="Арт", description="Арт из таблицы"
    )
    @commands.guild_only()
    async def арт(self, ctx, *, таблица: str = ""):

        # links to images are taken from the Google spreadsheet sheet, the name of which was specified by the user
        if таблица == "":
            await ctx.send(f"{ctx.message.author.mention}, укажите имя таблицы")
        else:
            try:
                await ctx.message.delete()
                pass
            except nextcord.errors.Forbidden:
                pass

            await ctx.send(self.bot.tables.get_art(ctx.guild.id, таблица))


def setup(bot):
    bot.add_cog(Arts(bot))
