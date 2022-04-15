from .connector import connectToDatabase, getSession
from sqlalchemy.ext.declarative import declarative_base
from .db_classes import ServerSettings as SS


def getInfo(session, guildid):
    # session = getSession(engine)
    x = getInfoBySession(session, guildid)
    if x is None:
        addInfo(session, guildid)
        x = getInfoBySession(session, guildid)
    # session.close()
    return x


def getInfoBySession(session, guildid):
    ServerSettings = SS
    ServerSettings.__tablename__ = f"{ServerSettings.__tablename__}-{guildid}"
    x = session.query(ServerSettings).get(guildid)
    return x


def addInfo(session, guildid):
    ServerSettings = SS
    ServerSettings.__tablename__ = f"{ServerSettings.__tablename__}-{guildid}"
    ServerSettings = ServerSettings()
    ServerSettings.uid = guildid
    ServerSettings.prefix = "="
    # session = getSession(engine)
    session.add(ServerSettings)
    session.commit()
    # session.close()


def getAdminRole(session, guildid):
    x = getInfo(session, guildid).adminroles
    if x is not None:
        x = x.split(",")
    return x


def addAdminRole(session, guildid, roleid):
    # session = getSession(engine)
    x = getInfoBySession(session, guildid)
    if x.adminroles is not None:
        x.adminroles += f"{roleid},"
    else:
        x.adminroles = f"{roleid},"

    session.commit()
    # session.close()


def addUserRole(session, guildid, roleid):
    # session = getSession(engine)
    x = getInfoBySession(session, guildid)
    if x.userroles is not None:
        x.userroles += f"{roleid},"
    else:
        x.userroles = f"{roleid},"

    session.commit()
    # session.close()


def delAdminRole(session, guildid, roleid):
    # session = getSession(engine)
    x = getInfo(session, guildid)
    if x.adminroles is not None:
        adminrole = x.adminroles.split(",")
        adminrole.remove(str(roleid))
        x.adminroles = (",").join(adminrole)
        session.commit()
    # session.close()


def getPrefix(session, guildid):
    return getInfo(session, guildid).prefix


def getAllPrefixes(session):
    prefixes = {}
    ServerSettings = SS
    ServerSettings.__tablename__ = f"{ServerSettings.__tablename__}-123"
    # session = getSession(engine)
    x = session.query(ServerSettings).all()
    for xe in x:
        prefixes[xe.uid] = xe.prefix
    # session.close()
    return prefixes


def getArtTable(session, guildid):
    x = getInfo(session, guildid).artspr
    if x is not None:
        return x
    else:
        return None


def getAstralTable(session, guildid):
    x = []
    try:
        x.append(getInfo(session, guildid).astralspr)
        x.append(getInfo(session, guildid).astralscr)
        return x
    except:
        return None


def getEmbTable(session, guildid):
    x = getInfo(session, guildid).embtable
    if x is not None:
        return x
    else:
        return None


def setPrivateVoice(session, guildid, vc):
    # session = getSession(engine)
    x = getInfoBySession(session, guildid)
    try:
        x.voicegenerator = vc[0]
        x.voicecategory = vc[1]
        session.commit()
        # session.close()
        return "Success"
    except Exception as e:
        # session.close()
        return f"Error: {e}"


def setPrefix(session, guildid, prefix):
    # session = getSession(engine)
    x = getInfoBySession(session, guildid)
    try:
        x.prefix = prefix
        session.commit()
        # session.close()
        return "Success"
    except Exception as e:
        # session.close()
        return f"Error: {e}"


def setAstralTable(session, guildid, ast):
    # session = getSession(engine)
    x = getInfoBySession(session, guildid)
    try:
        x.astralspr = ast
        session.commit()
        # session.close()
        return "Success"
    except Exception as e:
        session.close()
        return f"Error: {e}"


def setAstralScript(session, guildid, scr):
    # session = getSession(engine)
    x = getInfoBySession(session, guildid)
    try:
        x.astralscr = scr
        session.commit()
        # session.close()
        return "Success"
    except Exception as e:
        session.close()
        return f"Error: {e}"


def setRoles(session, guildid, roles):
    # session = getSession(engine)
    x = getInfoBySession(session, guildid)
    try:
        x.boyrole = roles[0]
        x.girlrole = roles[1]
        session.commit()
        # session.close()
        return "Success"
    except Exception as e:
        session.close()
        return f"Error: {e}"


def setArtTable(session, guildid, table):
    # session = getSession(engine)
    x = getInfoBySession(session, guildid)
    try:
        x.artspr = table
        session.commit()
        # session.close()
        return "Success"
    except Exception as e:
        session.close()
        return f"Error: {e}"


def setEmbTable(session, guildid, table):
    # session = getSession(engine)
    x = getInfoBySession(session, guildid)
    try:
        x.embtable = table
        session.commit()
        # session.close()
        return "Success"
    except Exception as e:
        return f"Error: {e}"


def getHoro(session):
    m = []
    x = session.query(SS).filter(SS.horo == True)
    for xy in x:
        m.append([xy.horochannel, xy.hororole])

    return m


def getHoroRole(session, guildid):
    return getInfo(session, guildid).hororole


def getHoroChannel(session, guildid):
    return getInfo(session, guildid).horochannel


def getHoroStatus(session, guild):
    return getInfo(session, guild).horo


def setHoro(session, guildid, f: bool, uid: int):
    x = getInfo(session, guildid)
    try:
        x.horo = f
        x.horochannel = uid
        session.commit()
    except Exception as e:
        return f"Error: {e}"


def setHoroRole(session, guildid, role):
    x = getInfo(session, guildid)
    try:
        x.hororole = role
        session.commit()
    except Exception as e:
        return f"Error: {e}"


def getVoiceSettingsMessage(session, guild):
    return getInfo(session, guild).voicemessage


def setVoiceSettingsMessage(session, guild, id):
    x = getInfo(session, guild)
    try:
        x.voicemessage = id
        session.commit()
    except Exception as e:
        return f"Error: {e}"


def getShikimoriNews(session):
    m = []
    x = session.query(SS).filter(SS.shikinews == True)
    for xy in x:
        m.append(xy.shikinewschannel)

    return m


def getShikimoriRelease(session):
    m = []
    x = session.query(SS).filter(SS.shikirelease == True)
    for xy in x:
        m.append(xy.shikireleasechannel)

    return m


def setShikimoriNews(session, guildid, f: bool, uid: int):
    x = getInfo(session, guildid)
    try:
        x.shikinews = f
        x.shikinewschannel = uid
        session.commit()
    except Exception as e:
        return f"Error: {e}"


def setShikimoriRelease(session, guildid, f: bool, uid: int):
    x = getInfo(session, guildid)
    try:
        x.shikirelease = f
        x.shikireleasechannel = uid
        session.commit()
    except Exception as e:
        return f"Error: {e}"


def getShikimoriNewsStatus(session, guild):
    return getInfo(session, guild).shikinews


def getShikimoriReleaseStatus(session, guild):
    return getInfo(session, guild).shikirelease
