from dataclasses import dataclass
from typing import Any, Callable, Optional

import nextcord.ext.commands
from modules.checkers import (
    check_admin_permissions,
    check_editor_permission,
    check_moderator_permission,
)
from nextcord import (
    BaseApplicationCommand,
    ClientCog,
    Interaction,
    SlashApplicationCommand,
)
from nextcord.ext.commands.cog import Cog

MISSING: Any = nextcord.utils.MISSING


@dataclass
class Command:
    name: str
    type: str
    brief: Optional[str]
    description: Optional[str]
    required_permission: Optional[str]


class MilkSlashCommand(SlashApplicationCommand):
    def __init__(
        self,
        callback: Callable,
        name: Optional[str] = None,
        brief: Optional[str] = None,
        description: Optional[str] = None,
        required_permission: Optional[str] = "",
        cog_name: Optional[str] = "",
        ignore_guilds: list[int] = None,
        only_at_guilds: list[int] = None,
        guild_only=True,
    ):
        super().__init__(
            callback=callback,
            name=name,
            name_localizations=None,
            description=brief,
            description_localizations=None,
            guild_ids=only_at_guilds,
            dm_permission=not guild_only,
            default_member_permissions=None,
            force_global=True if not only_at_guilds else False,
        )

        self.command_cog_name = cog_name
        self.command_type = "slash"
        self.brief = description
        self.description = description
        self.required_permission: Optional[str] = required_permission
        self.ignore_guilds = ignore_guilds if ignore_guilds is not None else []
        self.only_at_guilds = only_at_guilds if only_at_guilds is not None else []
        self.parent_cog: MilkCog
        self.aliases = []
        match required_permission:
            case "admin":
                self.permission_checker = check_admin_permissions
            case "moderator":
                self.permission_checker = check_moderator_permission
            case "editor":
                self.permission_checker = check_editor_permission
            case _:
                self.permission_checker: Optional[Callable] = None

    async def maybe_run(self, interaction: Interaction) -> bool:
        cog = self.parent_cog
        cog: MilkCog | ClientCog
        if (
            interaction.guild.id in cog.ignore_guilds
            or interaction.guild.id in self.ignore_guilds
        ):
            return False

        if cog.only_at_guilds and interaction.guild.id not in cog.only_at_guilds:
            return False

        if self.required_permission is None and isinstance(cog, MilkCog):
            match cog.required_permission:
                case "admin":
                    self.permission_checker = check_admin_permissions
                case "moderator":
                    self.permission_checker = check_moderator_permission
                case "editor":
                    self.permission_checker = check_editor_permission
        if self.permission_checker is not None:
            return await self.permission_checker(interaction, interaction.client)
        else:
            return True

    async def call(self, state, interaction) -> None:
        if await self.maybe_run(interaction):
            await super().call(state, interaction)
        else:
            await interaction.send("Недостаточно прав!", ephemeral=True)


class MilkMessageCommand(nextcord.ext.commands.Command):
    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls, *args, **kwargs)
        try:
            self.__original_kwargs__.pop("func")
        except:
            pass
        return self

    def __init__(
        self,
        func: Callable,
        name: Optional[str],
        brief: Optional[str],
        description: Optional[str],
        required_permission: Optional[str],
        cog_name: Optional[str],
        ignore_guilds: list[int],
        only_at_guilds: list[int],
        aliases: Optional[list[str]],
        guild_only=True,
    ):
        super().__init__(
            func,
            name=name,
            brief=brief,
            description=description,
            aliases=[] if aliases is None else aliases,
        )

        self.command_cog_name = cog_name
        self.command_type = "message"
        self.brief = brief
        self.description = description
        self.required_permission = required_permission
        self.ignore_guilds = ignore_guilds
        self.only_at_guilds = only_at_guilds
        self.guild_only = guild_only
        self.permission_checker = None
        match required_permission:
            case "admin":
                self.permission_checker = check_admin_permissions
            case "moderator":
                self.permission_checker = check_moderator_permission
            case "editor":
                self.permission_checker = check_editor_permission
            case _:
                self.permission_checker: Optional[Callable] = None

    async def maybe_run(self, ctx: nextcord.ext.commands.Context) -> bool:
        cog = self.cog
        cog: MilkCog
        if self.guild_only and ctx.guild is None:
            return False

        if ctx.guild.id in cog.ignore_guilds or ctx.guild.id in self.ignore_guilds:
            return False

        if cog.only_at_guilds and ctx.guild.id not in cog.only_at_guilds:
            return False

        if self.required_permission is None and isinstance(cog, MilkCog):
            match cog.required_permission:
                case "admin":
                    self.permission_checker = check_admin_permissions
                case "moderator":
                    self.permission_checker = check_moderator_permission
                case "editor":
                    self.permission_checker = check_editor_permission

        if self.permission_checker is not None:
            return await self.permission_checker(ctx)
        else:
            return True

    async def can_run(self, ctx: nextcord.ext.commands.Context) -> bool:
        if await self.maybe_run(ctx):
            return await super().can_run(ctx)
        else:
            return True


class MilkCog(Cog):
    bot: nextcord.ext.commands.Bot = None
    required_permission: Optional[str] = ""
    ignore_guilds: list[int] = []
    only_at_guilds: list[int] = []

    @staticmethod
    def slash_command(
        name: Optional[str] = None,
        brief: Optional[str] = None,
        permission: Optional[str] = "",
        description: Optional[str] = None,
        ignore_guilds: Optional[list[int]] = None,
        only_at_guilds: Optional[list[int]] = None,
    ):
        if ignore_guilds is None:
            ignore_guilds = []

        if only_at_guilds is None:
            only_at_guilds = []

        def decorator(func: Callable) -> MilkSlashCommand:
            if isinstance(func, BaseApplicationCommand):
                raise TypeError("Callback is already an application command.")

            app_cmd = MilkSlashCommand(
                callback=func,
                name=name,
                brief=brief,
                required_permission=permission,
                cog_name=func.__qualname__.split(".")[0],
                description=description,
                ignore_guilds=ignore_guilds,
                only_at_guilds=only_at_guilds,
            )

            return app_cmd

        return decorator

    @staticmethod
    def message_command(
        name: Optional[str] = None,
        brief: Optional[str] = None,
        description: Optional[str] = "",
        permission: Optional[str] = "",
        ignore_guilds: list[int] = None,
        only_at_guilds: list[int] = None,
        aliases: list[str] = None,
    ):
        def decorator(func: Callable) -> MilkMessageCommand:
            if isinstance(func, MilkMessageCommand):
                raise TypeError("Callback is already a command.")

            app_cmd = MilkMessageCommand(
                func=func,
                name=name,
                brief=brief,
                description=description,
                required_permission=permission,
                cog_name=func.__qualname__.split(".")[0],
                ignore_guilds=ignore_guilds if ignore_guilds is not None else [],
                only_at_guilds=only_at_guilds if only_at_guilds is not None else [],
                aliases=aliases if aliases is not None else [],
            )

            return app_cmd

        return decorator
