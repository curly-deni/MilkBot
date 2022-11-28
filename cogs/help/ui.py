import nextcord


class HelpPaginatior(nextcord.ui.View):
    def __init__(
        self,
        message: nextcord.Message,
        author: nextcord.Member,
        embeds,
    ):
        super().__init__(timeout=180.0)

        self.message: nextcord.Message = message
        self.author: nextcord.Member = author
        self.embeds = embeds
        self.embeds_dict = {}

        options: list[nextcord.SelectOption] = []
        main = self.embeds.pop(len(self.embeds) - 1)
        options.append(
            nextcord.SelectOption(
                label=main.name,
                description=main.description,
                emoji=main.emoji,
                value=main.name,
            )
        )
        self.embeds_dict[main.name] = main.embed
        for trans_data in self.embeds:
            options.append(
                nextcord.SelectOption(
                    label=trans_data.name,
                    description=trans_data.description,
                    emoji=trans_data.emoji,
                    value=trans_data.name,
                )
            )
            self.embeds_dict[trans_data.name] = trans_data.embed

        self.selector: nextcord.ui.Select = nextcord.ui.Select(
            placeholder="Раздел справки", options=options
        )
        self.add_item(self.selector)

    async def interaction_check(self, interaction: nextcord.Interaction):
        if interaction.user != self.author:
            return await interaction.send(
                "Вы не имеете право на это действие", ephemeral=True
            )

        embed_name = self.selector.values[0]
        await self.message.edit(embed=self.embeds_dict[embed_name])
        return True

    async def on_timeout(self) -> None:
        if isinstance(self.message, nextcord.Message):
            self.selector.disabled = True
            try:
                await self.message.edit(view=self)
            except:
                pass
