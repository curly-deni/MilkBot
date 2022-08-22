import nextcord
from typing import Optional


class FieldModal(nextcord.ui.Modal):
    def __init__(
        self,
        title: Optional[str] = None,
        label: Optional[str] = None,
        placeholder: Optional[str] = None,
    ):
        super().__init__(title=title, timeout=60.0)

        self.field = nextcord.ui.TextInput(
            label=label,
            placeholder=placeholder,
            required=True,
        )
        self.add_item(self.field)

    async def callback(self, interaction: nextcord.Interaction):
        # await interaction.send("Spell delivered", ephemeral=True)
        self.stop()

    def value(self) -> Optional[str]:
        return self.field.value
