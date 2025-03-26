from typing import Optional

from nextcord import Guild, Client, Embed, File
from nextcord.abc import Messageable, User
from nextcord.ext.commands import Context
from nextcord.ui import View

from .abstract_context import AbstractContext


class MessageContext(AbstractContext):

    def __init__(self, ctx: Context):
        self._ctx = ctx

    async def send_indication(self):
        await self._ctx.trigger_typing()

    async def send(
        self,
        content: Optional[str] = None,
        *,
        tts: bool = False,
        embed: Embed = None,
        embeds: list[Embed] = None,
        file: File = None,
        files: list[File] = None,
        delete_after: float = None,
        view: View = None,
        ephemeral: bool = False
    ):
        return await self._ctx.send(
            content=content,
            tts=tts,
            embed=embed,
            file=file,
            delete_after=delete_after,
            view=view,
        )

    @property
    def user(self) -> User:
        return self._ctx.author

    @property
    def client(self) -> Client:
        return self._ctx.bot

    @property
    def channel(self) -> Messageable:
        return self._ctx.channel

    @property
    def guild(self) -> Optional[Guild]:
        return self._ctx.guild

    @property
    def command(self):
        return self._ctx.command

    @property
    def locale(self) -> str:
        return "ru"
