from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine


from .db_classes import getShikimoriClass


def getInfo(session, guildid, uid):
    # session = getSession(engine)
    x = getInfoBySession(session, guildid, uid)
    # session.close()
    return x


def getInfoBySession(session, guildid, id):
    Shikimori = getShikimoriClass(guildid)
    return session.query(Shikimori).get(id)


def addInfo(session, guildid, uid, sid):
    x = getInfoBySession(session, guildid, uid)
    if x is not None:
        # session = getSession(engine)
        x.sid = sid
    else:
        Shikimori = getShikimoriClass(guildid)
        Shikimori = Shikimori()
        Shikimori.id = uid
        Shikimori.sid = sid
        session.add(Shikimori)
    session.commit()
    # session.close()


def getAllInfo(session, guildid):
    Shikimori = getShikimoriClass(guildid)
    return session.query(Shikimori).all()


def getSid(session, guildid, uid):
    x = getInfoBySession(session, guildid, uid)
    if x is None:
        return None
    else:
        return x.sid


def setSid(session, guildid, uid, sid):
    # session = getSession(engine)
    x = getInfoBySession(session, guildid, uid)
    if x is None:
        addInfo(session, guildid, uid, sid)
    else:
        x.sid = sid
        session.commit()
        # session.close()
