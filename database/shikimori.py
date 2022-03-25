from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine


from .db_classes import getShikimoriClass


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
    if x != None:
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
    if x == None:
        return False
    else:
        return x.sid


def setSid(session, guildid, uid, sid):
    # session = getSession(engine)
    x = getInfoBySession(session, guildid, uid)
    if x == None:
        addInfo(session, guildid, uid, sid)
    else:
        x.sid = sid
        session.commit()
        # session.close()
