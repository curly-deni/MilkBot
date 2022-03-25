from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from .db_classes import ServerSettings as SS


def connectToDatabase(uri, engine):
    if engine != None:
        enginex = engine.get_bind()
        engine.close()
        enginex.dispose()

    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)

    engine = create_engine(uri)

    engine.execute("ROLLBACK")

    return getSession(engine)


def getSession(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def getInfo(session, guildid):
    # session = getSession(engine)
    x = getInfoBySession(session, guildid)
    if x == None:
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
    if x != None:
        x = x.split(",")
    return x


def addAdminRole(session, guildid, roleid):
    # session = getSession(engine)
    x = getInfoBySession(session, guildid)
    if x.adminroles != None:
        x.adminroles += f"{roleid},"
    else:
        x.adminroles = f"{roleid},"

    session.commit()
    # session.close()


def addUserRole(session, guildid, roleid):
    # session = getSession(engine)
    x = getInfoBySession(session, guildid)
    if x.userroles != None:
        x.userroles += f"{roleid},"
    else:
        x.userroles = f"{roleid},"

    session.commit()
    # session.close()


def delAdminRole(session, guildid, roleid):
    # session = getSession(engine)
    x = getInfo(session, guildid)
    if x.adminroles != None:
        adminrole = x.adminroles.split(",")
        adminrole.delete(str(roleid))
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
    if x != None:
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
    if x != None:
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
