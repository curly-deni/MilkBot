from sqlalchemy import create_engine, desc
from sqlalchemy.orm import scoped_session, sessionmaker
from .db_classes import getStatClass
import datetime


def nlvl(lvl):
    if lvl != 0:
        return (5 * lvl**2 + 50 * lvl + 100) + nlvl(lvl - 1)
    else:
        return 5 * lvl**2 + 50 * lvl + 100


def countnewlvl(lvl, xp):
    nxp = nlvl(lvl)
    if xp > nxp:
        return countnewlvl(lvl + 1, xp)
    else:
        return lvl


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
    if x != None:
        # session.close()
        return x
    else:
        addInfo(session, guildid, uid)
        Stat = getStatClass(guildid)
        # session = getSession(engine)
        e = session.query(Stat).get(uid)
        # session.close()
        return e


def getAllInfoSorted(session, guildid):
    Stat = getStatClass(guildid)
    x = session.query(Stat).order_by(desc(Stat.xp))
    return x


def getInfoBySession(session, guildid, uid):
    Stat = getStatClass(guildid)
    x = session.query(Stat).get(uid)
    return x


def addInfo(session, guildid, uid):
    Stat = getStatClass(guildid)
    # session = getSession(engine)
    x = session.query(Stat).get(uid)
    if x != None:
        session.delete(x)
        # session.commit()
    try:
        Statx = Stat()
        Statx.uid = uid
        Statx.background = "https://raw.githubusercontent.com/I-dan-mi-I/images/main/cards/анемония.png"
        Statx.coin = 0
        Statx.quotex = "ваша цитата"
        Statx.color = "white"
        Statx.xp = 0
        Statx.lvl = 0
        session.add(Statx)
        session.commit()
        # session.close()
    except Exception as e:
        print(e)


def addBalls(session, guildid, uid, balls):
    # session = getSession(engine)
    x = getInfoBySession(session, guildid, uid)
    x.coin = str(int(x.coin) + balls)
    session.commit()
    # session.close()


def setBackground(session, guildid, uid, background):
    # session = getSession(engine)
    x = getInfoBySession(session, guildid, uid)
    x.background = background
    session.commit()
    # session.close()


def setColor(session, guildid, uid, color):
    # session = getSession(engine)
    x = getInfoBySession(session, guildid, uid)
    x.color = color
    session.commit()
    # session.close()


def setQuote(session, guildid, uid, Quote):
    # session = getSession(engine)
    x = getInfoBySession(session, guildid, uid)
    x.quotex = Quote
    session.commit()
    # session.close()


def addXp(session, guildid, uid, xp):
    # session = getSession(engine)
    x = getInfo(session, guildid, uid)
    if x.lvl == None:
        x.lvl = 0
    if (
        countnewlvl(x.lvl, x.xp + xp) != x.lvl
        and countnewlvl(x.lvl, x.xp + xp) - x.lvl > 0
    ):
        addLvl(session, guildid, uid, countnewlvl(x.lvl, x.xp + xp) - x.lvl)
    x.xp += round(xp)
    session.commit()
    # session.close()


def addLvl(session, guildid, uid, lvl):
    x = getInfo(session, guildid, uid)
    if x.lvl == None:
        x.lvl = lvl
    else:
        x.lvl += lvl
    session.commit()


def addCookie(session, guildid, uid):
    x = getInfo(session, guildid, uid)
    if x.cookie == None:
        x.cookie = 1
    else:
        x.cookie += 1
    session.commit()


def addVoiceTime(session, guildid, uid, time):
    x = getInfo(session, guildid, uid)
    if x.allvoicetime == None:
        x.allvoicetime = time
    else:
        x.allvoicetime += time
    session.commit()


def setLvl(session, guildid, uid, lvl):
    # session = getSession(engine)
    x = getInfo(session, guildid, uid)
    x.lvl = lvl
    session.commit()
    # session.close()


def setVoiceConnectTime(session, guildid, uid, time):
    # session = getSession(engine)
    x = getInfoBySession(session, guildid, uid)
    x.voiceconn = time
    session.commit()
    # session.close()
