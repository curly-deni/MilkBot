from nextcord import Role, Member
from nextcord.ext.commands import Context


def __have_common_parts(user_roles: list[Role], roles: list[int]) -> bool:
    user_roles_ids: set = {role.id for role in user_roles}
    common_parts: list = list(user_roles_ids & set(roles))
    return len(common_parts) != 0


def check_editor_permission(ctx: Context) -> bool:
    if ctx.author.guild_permissions.administrator:
        return True
    else:
        roles = []
        roles_dict = ctx.bot.database.get_stuff_roles(ctx.guild.id)
        for key in list(roles_dict.keys()):
            roles += roles_dict[key]

        return __have_common_parts(
            ctx.author.roles,
            roles,
        )


def check_moderator_permission(ctx: Context) -> bool:
    if ctx.author.guild_permissions.administrator:
        return True
    else:
        roles = ctx.bot.database.get_stuff_roles(ctx.guild.id)
        return __have_common_parts(
            ctx.author.roles,
            (roles["moderator"] + roles["admin"])
            if roles["moderator"] or roles["admin"]
            else [],
        )


def check_admin_permissions(ctx: Context) -> bool:
    if ctx.author.guild_permissions.administrator:
        return True
    else:
        roles = ctx.bot.database.get_stuff_roles(ctx.guild.id)
        return __have_common_parts(ctx.author.roles, roles["admin"])


def is_stuff(bot, member: Member) -> bool:
    roles = bot.database.get_stuff_roles(member.guild.id)
    return __have_common_parts(member.roles, roles["moderator"] + roles["admin"])
