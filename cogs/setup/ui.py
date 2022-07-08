import nextcord


class SettingsViewer(nextcord.ui.View):
    def __init__(self, author: nextcord.Member, embed: nextcord.Embed):
        super().__init__(timeout=180.0)

        self.author: nextcord.Member = author
        self.embed: nextcord.Embed = embed

        self.send_button: nextcord.ui.Button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.green, label="Отправить настройки"
        )

        self.add_item(self.send_button)

    async def interaction_check(self, interaction: nextcord.Interaction):
        if interaction.user != self.author:
            return await interaction.send(
                "Вы не имеете право на это действие", ephemeral=True
            )

        return await interaction.send(embed=self.embed, ephemeral=True)
