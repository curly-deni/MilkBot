from .connector import connectToDatabase, getSession

from .db_classes import getGenshinClass
from sqlalchemy import Column, Integer, String


def getInfo(session, guildid, uid):
    # session = getSession(engine)
    x = getInfoBySession(session, guildid, uid)
    # session.close()
    return x


def getInfoBySession(session, guildid, uid):
    Genshin = getGenshinClass(guildid)
    return session.query(Genshin).get(uid)


def addInfo(session, guildid, uid, mihoyouid, genshinuid, genshinname, discordname, ar):
    # session = getSession(engine)
    Genshin = getGenshinClass(guildid)
    Genshin = Genshin()
    Genshin.uid = uid
    Genshin.color_stat = "white"
    Genshin.color_name = "white"
    Genshin.color_titles = "white"
    Genshin.background = (
        "https://raw.githubusercontent.com/I-dan-mi-I/images/main/banners/новый мир.png"
    )
    Genshin.mihoyouid = mihoyouid
    Genshin.genshinuid = genshinuid
    Genshin.genshinname = genshinname
    Genshin.discordname = discordname
    Genshin.ar = ar
    session.add(Genshin)
    session.commit()
    # session.close()


def setBackground(session, guildid, uid, background):
    # session = getSession(engine)
    x = getInfoBySession(session, guildid, uid)
    if x is None:
        return False
    else:
        x.background = background
        session.commit()
        # session.close()
        return True


def setColor(session, guildid, uid, color):
    # session = getSession(engine)
    x = getInfoBySession(session, guildid, uid)
    if x is None:
        return False
    else:
        x.color_stat = (color[0],)
        x.color_name = (color[1],)
        x.color_titles = (color[2],)
        session.commit()
        # session.close()
        return True
