from database.serversettings import getAdminRole


def check_permission(userroleslist, adminroleslist):
    for x in userroleslist:
        if adminroleslist is not None:
            if str(x.id) in adminroleslist:
                return True
    return False


def isAdmin(userroleslist, adminroleslist):
    return check_permission(userroleslist, adminroleslist)


def check_admin_permissions(ctx):
    if ctx.author.guild_permissions.administrator:
        return True
    else:
        return check_permission(
            ctx.author.roles, getAdminRole(ctx.bot.databaseSession, ctx.guild.id)
        )
