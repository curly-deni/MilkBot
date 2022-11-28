from dataclasses import dataclass
from typing import Optional, Union

import nextcord


@dataclass
class Button:
    button: nextcord.ui.Button
    value: Union[str, int, nextcord.Role]


class SelectRole(nextcord.ui.View):
    def __init__(
        self, author: Union[nextcord.Member, nextcord.User], roles: list[nextcord.Role]
    ):
        super().__init__(timeout=180.0)

        self.value: Optional[str] = None
        self.author = author

        self.message: Optional[
            Union[nextcord.PartialInteractionMessage, nextcord.WebhookMessage]
        ] = None

        self.buttons = {}
        for role in roles:
            button = nextcord.ui.Button(label=role.name)
            self.buttons[button.custom_id] = Button(button=button, value=role)
            self.add_item(self.buttons[button.custom_id].button)

    async def interaction_check(self, interaction: nextcord.Interaction):
        if interaction.user != self.author:
            return await interaction.send("Недоступное действие!")
        button = self.buttons.get(interaction.data["custom_id"], None)
        if button is None:
            return True
        self.value = button.value
        await self.on_timeout()
        self.stop()
        return True

    async def on_timeout(self) -> None:
        if isinstance(self.message, nextcord.PartialInteractionMessage) or isinstance(
            self.message, nextcord.WebhookMessage
        ):
            for child in self.children:
                try:
                    child.disabled = True
                except:
                    continue
            try:
                await self.message.edit(view=self)
            except:
                pass
