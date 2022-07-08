import nextcord


class FieldModal(nextcord.ui.Modal):
    def __init__(self, title=None, label=None, placeholder=None):
        super().__init__(title=title, timeout=60.0)

        self.field: nextcord.ui.TextInput = nextcord.ui.TextInput(
            label=label, placeholder=placeholder, required=True
        )
        self.add_item(self.field)

    async def callback(self, interaction: nextcord.Interaction):
        self.stop()

    def value(self):
        return self.field.value
