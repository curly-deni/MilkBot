from framecho.bot import Bot
from framecho.context.abstract_context import AbstractContext


@Bot.add_permission_checker("admin")
async def is_admin(ctx: AbstractContext) -> bool:
    return True


@Bot.add_permission_checker("moderator")
async def is_moderator(ctx: AbstractContext) -> bool:
    return True


@Bot.add_permission_checker("editor")
async def is_editor(ctx: AbstractContext) -> bool:
    return True


@Bot.add_permission_checker("guild_owner")
async def is_guild_owner(ctx: AbstractContext) -> bool:
    if not ctx.guild:
        return False

    return ctx.guild.owner_id == ctx.user.id


@Bot.add_permission_checker("bot_owner")
async def is_bot_owner(ctx: AbstractContext) -> bool:
    return ctx.client.owner_id == ctx.user.id  # noqa
