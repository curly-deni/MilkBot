import nextcord


class PaginationSelectors(nextcord.ui.View):
    def __init__(
        self,
        message: nextcord.Message,
        author: nextcord.Member,
        stat_embeds: dict,
        character_embeds: dict,
    ):
        super().__init__(timeout=180.0)

        self.message: nextcord.Message = message

        self.author: nextcord.Member = author
        self.stat_embeds: dict = stat_embeds
        self.character_embeds: dict = character_embeds

        stat_options: list[nextcord.SelectOption] = []
        for embed_name in self.stat_embeds:
            stat_options.append(
                nextcord.SelectOption(label=embed_name, value=embed_name)
            )

        self.stat_selector: nextcord.ui.Select = nextcord.ui.Select(
            placeholder="Раздел статистики", options=stat_options
        )

        character_options: list[nextcord.SelectOption] = []
        for embed_name in self.character_embeds:
            character_options.append(
                nextcord.SelectOption(label=embed_name, value=embed_name)
            )

        self.character_selector: nextcord.ui.Select = nextcord.ui.Select(
            placeholder="Персонаж", options=character_options
        )

        self.add_item(self.stat_selector)
        self.add_item(self.character_selector)

    async def interaction_check(self, interaction: nextcord.Interaction):
        if interaction.user != self.author:
            return await interaction.send(
                "Вы не имеете право на это действие", ephemeral=True
            )

        match interaction.data["custom_id"]:
            case self.stat_selector.custom_id:
                if not self.stat_selector.values:
                    return True

                embed_name = self.stat_selector.values[
                    len(self.stat_selector.values) - 1
                ]
                await self.message.edit(embed=self.stat_embeds[embed_name])
            case self.character_selector.custom_id:
                if not self.character_selector.values:
                    return True

                embed_name = self.character_selector.values[
                    len(self.character_selector.values) - 1
                ]
                await self.message.edit(embed=self.character_embeds[embed_name])
        return True
