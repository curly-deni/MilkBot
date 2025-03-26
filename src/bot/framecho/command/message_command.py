from typing import Callable

from nextcord.ext.commands import Command, Context

from framecho.command.abstract_command import AbstractCommand
from framecho.context.abstract_context import AbstractContext
from framecho.context.message_context import MessageContext
from framecho.option import Option


class MessageCommand(Command, AbstractCommand):
    CORE_CONTEXT_CLASS = Context

    def __init__(
        self,
        callback: Callable,
        *,
        nsfw: bool = False,
        force_global: bool = False,
        guild_ids: list[int] = None,
        guild_only: bool = True,
    ) -> None:
        AbstractCommand.__init__(
            self,
            callback,
            nsfw=nsfw,
            guild_ids=guild_ids,
            guild_only=guild_only,
            force_global=force_global,
        )
        Command.__init__(
            self,
            func=self._callback,
            name=callback.__name__,
            brief="",
            description="",
            aliases=[],
        )

    @staticmethod
    def _get_options(option: Option) -> dict:
        return option.message_option

    def _process_ctx(self, ctx) -> AbstractContext:
        return MessageContext(ctx)
