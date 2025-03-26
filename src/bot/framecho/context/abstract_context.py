from abc import ABC
from typing import Optional

from nextcord import Client, Guild, Embed, File, TextInputStyle, ButtonStyle
from nextcord.abc import Messageable, User
from nextcord.ui.view import View

from sqlalchemy.ext.asyncio import AsyncSession

from framecho.ui.asker import Asker, AskerView


class AbstractContext(ABC):
    db_session: Optional[AsyncSession] = None
    _ephemeral = True

    @property
    def ephemeral(self):
        return self._ephemeral

    @ephemeral.setter
    def ephemeral(self, value: bool):
        if not isinstance(value, bool):
            raise TypeError("ephemeral must be a bool")

        self._ephemeral = value

    async def send_indication(self):
        raise NotImplementedError

    async def send_asker(
        self,
        asker: Asker,
        *,
        embed: Optional[Embed] = None,
        text: Optional[str] = None,
        button_text: Optional[str] = None,
        button_emoji: Optional[str] = None,
        button_style: ButtonStyle = ButtonStyle.green,
        timeout: Optional[float] = 60
    ) -> dict:
        view = AskerView(
            self.user,
            asker,
            button_text=button_text,
            button_emoji=button_emoji,
            button_style=button_style,
            timeout=timeout,
        )
        await self.send(
            text if text else asker.title, view=view, embed=embed, ephemeral=True
        )
        await asker.wait()

        return asker.value

    async def ask(
        self,
        title: str,
        question: str,
        *,
        timeout: Optional[float] = None,
        style: TextInputStyle = TextInputStyle.short,
        min_length: int = 0,
        max_length: int = 4000,
        required: bool = False,
        default_value: Optional[str] = None
    ):
        asker = Asker(title, timeout=timeout)
        key = "question"
        asker.add_question(
            key,
            question,
            style=style,
            min_length=min_length,
            max_length=max_length,
            required=required,
            default_value=default_value,
        )

        values_dict = await self.send_asker(asker)

        return values_dict[key]

    async def send(
        self,
        content: Optional[str] = None,
        *,
        tts: bool = False,
        embed: Embed = None,
        file: File = None,
        delete_after: float = None,
        view: View = None,
        ephemeral: bool = False
    ):
        raise NotImplementedError

    @property
    def user(self) -> User:
        raise NotImplementedError

    @property
    def client(self) -> Client:
        raise NotImplementedError

    @property
    def channel(self) -> Messageable:
        raise NotImplementedError

    @property
    def guild(self) -> Optional[Guild]:
        raise NotImplementedError

    @property
    def command(self):
        raise NotImplementedError

    @property
    def locale(self) -> str:
        raise NotImplementedError
