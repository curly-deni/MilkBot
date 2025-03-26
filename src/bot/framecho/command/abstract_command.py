from abc import ABC
from functools import wraps
from inspect import signature, Signature
from typing import Callable, Optional

from framecho.context.abstract_context import AbstractContext
from framecho.option import Option


class AbstractCommand(ABC):
    CORE_CONTEXT_CLASS = None

    def __init__(
        self,
        callback: Callable,
        *,
        permissions: list[str] = None,
        nsfw: bool = False,
        force_global: bool = False,
        guild_ids: list[int] = None,
        guild_only: bool = True,
    ) -> None:
        self._raw_callback = callback
        self._callback = self._decorate_callback_with_runner()
        self._nsfw = nsfw
        self._force_global = force_global
        self._guild_ids = guild_ids if guild_ids else []
        self._guild_only = guild_only
        self._permissions = permissions if permissions else []

    async def _runner(self, *args, **kwargs):

        # convert nextcord Context or Interaction to CustomContext
        original_ctx = args[1]

        if not isinstance(original_ctx, AbstractContext):
            converted_ctx = self._process_ctx(original_ctx)
        else:
            converted_ctx = original_ctx

        is_runnable_report = await self.is_runnable(converted_ctx)

        if not is_runnable_report["runnable"]:
            return await self._process_none_runnable(
                converted_ctx, is_runnable_report["reason"]
            )

        # modify arguments
        args = (args[0], converted_ctx) + args[2:]

        # noinspection PyUnresolvedReferences
        async with converted_ctx.client.session_maker() as session:
            converted_ctx.db_session = session
            try:
                return await self._raw_callback(*args, **kwargs)
            except Exception as e:
                await session.rollback()
                raise e

    def _decorate_callback_with_runner(self):
        func = self._raw_callback
        sig = signature(func)

        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await self._runner(*args, **kwargs)

        wrapper.__signature__ = self._process_signature(sig)
        return wrapper

    @staticmethod
    def _get_options(option: Option) -> dict:
        raise NotImplementedError

    def _process_signature(self, sig: Signature) -> Signature:
        new_parameters = {}

        for name, param in sig.parameters.items():
            if name == "ctx":
                new_parameters[name] = param.replace(annotation=self.CORE_CONTEXT_CLASS)
                continue

            if isinstance(param.default, Option):

                option = param.default
                option.load(name=name, type=param.annotation, kind=param.kind)

                new_parameters[name] = param.replace(**self._get_options(option))
                continue

            new_parameters[name] = param

        sig = sig.replace(parameters=list(new_parameters.values()))

        return sig

    def _process_ctx(self, ctx) -> AbstractContext:
        raise NotImplementedError

    async def _process_none_runnable(  # noqa
        self, ctx: AbstractContext, reason: Optional[str] = None
    ):
        return await ctx.send(
            f"This command is not runnable. Reason: {reason or 'unknown'}",
            ephemeral=True,
            delete_after=15,
        )

    async def is_runnable(self, ctx: AbstractContext) -> dict:

        if self._guild_only and not ctx.guild:
            return {
                "runnable": False,
                "reason": "guild_only",
            }

        if self._guild_ids and ctx.guild.id not in self._guild_ids:
            return {
                "runnable": False,
                "reason": "guild_ids",
            }

        if self._nsfw and (
            not hasattr(ctx.channel, "is_nsfw") or not ctx.channel.is_nsfw()  # noqa
        ):
            return {
                "runnable": False,
                "reason": "nsfw",
            }

        if self._permissions:
            checkers = ctx.client.permission_checkers  # noqa
            for permission in self._permissions:
                if permission not in checkers:
                    return {
                        "runnable": False,
                        "reason": f"Unable to check permission {permission}",
                    }
                if not await checkers[permission](ctx):
                    return {
                        "runnable": False,
                        "reason": f"Permission check {permission} failed",
                    }

        return {"runnable": True}
