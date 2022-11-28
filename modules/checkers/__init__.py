from nextcord import Interaction, Member, Role
from nextcord.ext.commands import Context


def __have_common_parts(user_roles: list[Role], roles: list[int]) -> bool:
    user_roles_ids: set = {role.id for role in user_roles}
    common_parts: list = list(user_roles_ids & set(roles))
    return len(common_parts) != 0


async def check_editor_permission(container: Context | Interaction, bot=None) -> bool:
    if isinstance(container, Context):
        user = container.author
        db = container.bot.database
    else:
        user = container.user
        db = bot.database

    if not isinstance(user, Member):
        return True

    if user.guild_permissions.administrator:
        return True
    else:
        roles = []
        roles_dict = db.get_stuff_roles(user.guild.id)
        for key in roles_dict:
            roles += roles_dict[key]

        return __have_common_parts(
            user.roles,
            roles,
        )


app_check_editor_permission = check_editor_permission


async def check_moderator_permission(
    container: Context | Interaction, bot=None
) -> bool:
    if isinstance(container, Context):
        user = container.author
        db = container.bot.database
    else:
        user = container.user
        db = bot.database

    if not isinstance(user, Member):
        return True

    if user.guild_permissions.administrator:
        return True
    else:
        roles = db.get_stuff_roles(user.guild.id)
        return __have_common_parts(
            user.roles,
            (roles["moderator"] + roles["admin"])
            if roles["moderator"] or roles["admin"]
            else [],
        )


app_check_moderator_permission = check_moderator_permission


async def check_admin_permissions(container: Context | Interaction, bot=None) -> bool:
    if isinstance(container, Context):
        user = container.author
        db = container.bot.database
    else:
        user = container.user
        db = bot.database

    if not isinstance(user, Member):
        return True

    if user.guild_permissions.administrator:
        return True
    else:
        roles = db.get_stuff_roles(user.guild.id)
        return __have_common_parts(user.roles, roles["admin"])


async def check_guild(container: Context | Interaction, bot=None) -> bool:
    return container.guild is not None


app_check_admin_permissions = check_admin_permissions


async def is_stuff(bot, member: Member) -> bool:
    roles = bot.database.get_stuff_roles(member.guild.id)
    return __have_common_parts(member.roles, roles["moderator"] + roles["admin"])
