from typing import Optional

import nextcord.utils
from nextcord import Interaction, Guild, Client, Embed, File, ButtonStyle
from nextcord.abc import Messageable, User
from nextcord.ui import View

from .abstract_context import AbstractContext
from framecho.ui.asker import Asker


class InteractionContext(AbstractContext):
    def __init__(self, interaction: Interaction):
        self._interaction = interaction

    async def send_indication(self):
        await self._interaction.response.defer(ephemeral=self._ephemeral)

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
        if self._interaction.response.is_done() or self._interaction.is_expired():
            return await super().send_asker(
                asker,
                embed=embed,
                text=text,
                button_text=button_text,
                button_emoji=button_emoji,
                button_style=button_style,
                timeout=timeout,
            )

        await self._interaction.response.send_modal(asker)
        await asker.wait()

        return asker.value

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
        return await self._interaction.send(
            content=content,
            tts=tts,
            embed=embed if embed else nextcord.utils.MISSING,
            file=file if file else nextcord.utils.MISSING,
            delete_after=delete_after,
            view=view if view else nextcord.utils.MISSING,
            ephemeral=ephemeral,
        )

    @property
    def user(self) -> User:
        return self._interaction.user

    @property
    def client(self) -> Client:
        return self._interaction.client

    @property
    def channel(self) -> Messageable:
        # noinspection PyTypeChecker
        return self._interaction.channel

    @property
    def guild(self) -> Optional[Guild]:
        return self._interaction.guild

    @property
    def command(self):
        return self._interaction.application_command

    @property
    def locale(self) -> str:
        return self._interaction.locale
