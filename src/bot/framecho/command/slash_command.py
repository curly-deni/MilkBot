from typing import Callable

from nextcord import SlashApplicationCommand, Interaction

from framecho.command.abstract_command import AbstractCommand
from framecho.context.abstract_context import AbstractContext
from framecho.context.interaction_context import InteractionContext
from framecho.option import Option


class SlashCommand(AbstractCommand, SlashApplicationCommand):
    CORE_CONTEXT_CLASS = Interaction

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
        SlashApplicationCommand.__init__(
            self,
            callback=self._callback,
            name=callback.__name__,
            name_localizations=None,
            description=None,
            description_localizations=None,
            guild_ids=self._guild_ids,
            force_global=self._force_global,
        )

    @staticmethod
    def _get_options(option: Option) -> dict:
        return option.slash_option

    def _process_ctx(self, ctx) -> AbstractContext:
        return InteractionContext(ctx)
