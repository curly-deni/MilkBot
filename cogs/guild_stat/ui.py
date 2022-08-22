import nextcord
from typing import Optional


def to_binary(a) -> list:
    l, m = [], []
    for i in a:
        l.append(ord(i))
    for i in l:
        m.append(int(bin(i)[2:]))
    return m


class QuoteApplier(nextcord.ui.View):
    def __init__(self, author: nextcord.Member):
        super().__init__(timeout=180.0)

        self.author: nextcord.Member = author
        self.quote: Optional[str] = None

        self.message: Optional[nextcord.Message] = None

        self.send_button: nextcord.ui.Button = nextcord.ui.Button(
            style=nextcord.ButtonStyle.green, label="Ввести цитату"
        )

        self.add_item(self.send_button)

    async def interaction_check(self, interaction: nextcord.Interaction):
        if interaction.user != self.author:
            return await interaction.send(
                "Вы не имеете право на это действие", ephemeral=True
            )

        modal = FieldModal(
            title="Статистика", label="Цитата пользователя", placeholder="Цитата"
        )

        try:
            await interaction.response.send_modal(modal)
        except:
            return

        await modal.wait()

        try:
            name: str = modal.value()
        except:
            return

        try:
            binary_name: list = to_binary(name)
        except:
            return

        if binary_name:
            self.quote = name
            await self.on_timeout()
            self.stop()
        else:
            try:
                await interaction.send("Вы не указали цитату", ephemeral=True)
            except:
                try:
                    await interaction.followup.send(
                        "Вы не указали цитату", ephemeral=True
                    )
                except:
                    return True

    async def on_timeout(self) -> None:
        self.send_button.disabled = True
        if isinstance(self.message, nextcord.Message):
            try:
                await self.message.edit(view=self)
            except:
                pass


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
