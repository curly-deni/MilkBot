def check_permission(userroleslist, adminroleslist):
    for x in userroleslist:
        if adminroleslist != None:
            if str(x.id) in adminroleslist:
                return True
    return False


def isAdmin(userroleslist, adminroleslist):
    return check_permission(userroleslist, adminroleslist)
