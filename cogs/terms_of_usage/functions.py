import nextcord
from nextcord.ext import commands
from nextcord.ext.commands import Context

from .phrases import privacy_policy, user_terms
from nextcord_paginator import Paginator


class TermsOfUsage(commands.Cog, name="Условия использования бота"):
    """Правовые требования для пользователей бота"""

    COG_EMOJI: str = "⚖️"

    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Отправка политики конфеденциальности")
    @commands.guild_only()
    async def политика_конфеденциальности(self, ctx: Context):

        return await self.send_paginated_phrases(
            ctx, "Политика в отношении обработки персональных данных", privacy_policy
        )

    @commands.command(brief="Отправка пользовательского соглашения")
    @commands.guild_only()
    async def пользовательское_соглашение(self, ctx: Context):
        return await self.send_paginated_phrases(
            ctx, "Пользовательское соглашение", user_terms
        )

    async def send_paginated_phrases(
        self, ctx: Context, phrases_theme: str, phrases_dict: dict
    ):
        embeds: list[nextcord.Embed] = []

        for chapter_name, chapter_text in phrases_dict.items():
            embeds.append(
                nextcord.Embed(
                    title=f"{phrases_theme}\n{chapter_name}"
                    if chapter_name != phrases_theme
                    else phrases_theme,
                    description=chapter_text,
                    colour=nextcord.Colour.dark_purple(),
                )
            )

        message = await ctx.author.send(embed=embeds[0])

        await ctx.send("Отправлено в ЛС!")

        page: Paginator = Paginator(
            message,
            embeds,
            ctx.author,
            self.bot,
            footerpage=True,
            footerdatetime=False,
            footerboticon=True,
            timeout=180.0,
        )
        try:
            await page.start()
        except nextcord.errors.NotFound:
            pass


def setup(bot):
    bot.add_cog(TermsOfUsage(bot))
