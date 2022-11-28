import nextcord
from base.base_cog import MilkCog
from modules.paginator import Paginator

from .phrases import privacy_policy, user_terms


class TermsOfUsage(MilkCog, name="Условия использования бота"):
    """Правовые требования для пользователей бота"""

    COG_EMOJI: str = "⚖️"

    def __init__(self, bot):
        self.bot = bot

    @MilkCog.slash_command(
        description="Политика конфеденциальности в отношении обработки персональных данных",
    )
    async def privacy_policy(self, interaction: nextcord.Interaction):
        await interaction.response.defer(ephemeral=True)

        return await self.send_paginated_phrases(
            interaction,
            "Политика в отношении обработки персональных данных",
            privacy_policy,
        )

    @MilkCog.slash_command(description="Пользовательское соглашение")
    async def user_terms(self, interaction: nextcord.Interaction):
        await interaction.response.defer(ephemeral=True)

        return await self.send_paginated_phrases(
            interaction, "Пользовательское соглашение", user_terms
        )

    async def send_paginated_phrases(
        self, interaction: nextcord.Interaction, phrases_theme: str, phrases_dict: dict
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

        message = await interaction.followup.send(embed=embeds[0])

        page: Paginator = Paginator(
            message,
            embeds,
            interaction.user,
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
