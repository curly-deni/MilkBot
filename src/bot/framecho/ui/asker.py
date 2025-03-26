from typing import Optional

from nextcord import TextInputStyle, Interaction, User, ButtonStyle
from nextcord.ui import Modal, TextInput, Item, Button

from .base import BaseView

BUTTON_TEXT = "Answer"
BUTTON_STYLE = ButtonStyle.green

__all__ = ["Asker", "AskerView"]


class Asker(Modal):

    def __init__(self, title: str, *, timeout: Optional[float] = None):
        super().__init__(title, timeout=timeout)

        self._items = {}
        self._defaults = {}

    def add_item(self, item: Item) -> Modal:
        raise NotImplementedError

    def add_question(
        self,
        key: str,
        question: str,
        *,
        style: TextInputStyle = TextInputStyle.short,
        min_length: int = 0,
        max_length: int = 4000,
        required: bool = False,
        default_value: Optional[str] = None,
        placeholder: Optional[str] = None,
    ):
        text_input = TextInput(
            label=question,
            style=style,
            min_length=min_length,
            max_length=max_length,
            required=required,
            placeholder=placeholder,
        )
        super().add_item(text_input)
        self._items[key] = text_input
        self._defaults[key] = default_value

        return self

    async def callback(self, interaction: Interaction):
        await interaction.response.defer(with_message=False)
        try:
            self.stop()
        except Exception as e:
            interaction.client.logger.error("Error when stop Asker Modal", e)

    @property
    def value(self):
        return {
            k: v.value if v.value is not None else self._defaults[k]
            for k, v in self._items.items()
        }


class AskerView(BaseView):

    def __init__(
        self,
        user: User,
        asker,
        *,
        button_text: str = BUTTON_TEXT,
        button_emoji: Optional[str] = None,
        button_style: ButtonStyle = ButtonStyle.green,
        private: bool = True,
        timeout: Optional[float] = 60,
    ):
        super().__init__(user, private=private, timeout=timeout, auto_defer=True)

        self._asker = asker
        self._button = Button(
            label=button_text if button_text else BUTTON_TEXT,
            emoji=button_emoji,
            style=button_style if button_style else BUTTON_STYLE,
        )

        super().add_item(self._button)

    def add_item(self, item: Item) -> None:
        raise NotImplemented

    async def callback(self, interaction: Interaction):
        await interaction.response.send_modal(self._asker)
