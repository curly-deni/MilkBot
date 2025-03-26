from functools import wraps
from typing import Callable

from nextcord.ext.commands import Cog as NCog

from framecho.bot import Bot
from framecho.command.abstract_command import AbstractCommand
from framecho.command.message_command import MessageCommand
from framecho.command.slash_command import SlashCommand
from framecho.hybrid_dispatcher import HybridDispatcher

__all__ = ["Cog"]


class Cog(HybridDispatcher, NCog):

    def __init__(self, bot: Bot):
        self._bot = bot
        self._on_load()

    def _on_load(self):
        pass

    @property
    def bot(self):
        return self._bot

    @staticmethod
    def message_command(
        *,
        permissions: list[str] = None,
        nsfw: bool = False,
        force_global: bool = False,
        guild_ids: list[int] = None,
        guild_only: bool = True,
    ):

        def decorator(func: Callable):
            return MessageCommand(
                func,
                nsfw=nsfw,
                force_global=force_global,
                guild_ids=guild_ids,
                guild_only=guild_only,
                # permissions=permissions
            )

        return decorator

    @staticmethod
    def slash_command(
        *,
        permissions: list[str] = None,
        nsfw: bool = False,
        force_global: bool = False,
        guild_ids: list[int] = None,
        guild_only: bool = True,
    ):

        def decorator(func: Callable):
            return SlashCommand(
                func,
                nsfw=nsfw,
                force_global=force_global,
                guild_ids=guild_ids,
                guild_only=guild_only,
                # permissions=permissions
            )

        return decorator

    @staticmethod
    def hybrid_command(
        *,
        slash_command: bool = True,
        message_command: bool = True,
        permissions: list[str] = None,
        nsfw: bool = False,
        force_global: bool = False,
        guild_ids: list[int] = None,
        guild_only: bool = True,
    ):

        def outer_decorator(func: Callable):

            @wraps(func)
            def inner_decorator() -> list[AbstractCommand]:
                ret: list[AbstractCommand] = []

                if message_command:
                    ret.append(
                        MessageCommand(
                            func,
                            nsfw=nsfw,
                            force_global=force_global,
                            guild_ids=guild_ids,
                            guild_only=guild_only,
                            # permissions=permissions
                        )
                    )

                if slash_command:
                    ret.append(
                        SlashCommand(
                            func,
                            nsfw=nsfw,
                            force_global=force_global,
                            guild_ids=guild_ids,
                            guild_only=guild_only,
                            # permissions=permissions
                        )
                    )

                return ret

            inner_decorator.hybrid = True
            return inner_decorator

        return outer_decorator
