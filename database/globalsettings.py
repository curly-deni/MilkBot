from .connector import connectToDatabase, getSession
from sqlalchemy.ext.declarative import declarative_base
from .db_classes import GlobalSettings


def getMasterPrefix(session):
    # session = getSession(engine)
    x = session.query(GlobalSettings).get(0).mprefix
    # session.close()
    return x


def getArtMasterTable(session):
    # session = getSession(engine)
    x = session.query(GlobalSettings).get(0).arttable
    # session.close()
    return x


def getAstralMasterTable(session):
    # session = getSession(engine)
    x = session.query(GlobalSettings).get(0).astraltable
    # session.close()
    return x


def getEmbMasterTable(session):
    # session = getSession(engine)
    x = session.query(GlobalSettings).get(0).embtable
    # session.close()
    return x


def setMasterPrefix(session, prefix):
    # session = getSession(engine)
    x = session.query(GlobalSettings).get(0)
    try:
        x.mprefix = prefix
        session.commit()
        # session.close()
        return "Success"
    except Exception as e:
        return f"Error: {e}"


def setAstralMasterTable(session, table):
    # session = getSession(engine)
    x = session.query(GlobalSettings).get(0)
    try:
        x.astraltable = table
        session.commit()
        # session.close()
        return "Success"
    except Exception as e:
        return f"Error: {e}"


def setEmbMasterTable(session, table):
    # session = getSession(engine)
    x = session.query(GlobalSettings).get(0)
    try:
        x.embtable = table
        session.commit()
        # session.close()
        return "Success"
    except Exception as e:
        return f"Error: {e}"


def getLastPublishedShikimoriNewsTime(session):
    return session.query(GlobalSettings).get(0).shikinewstime


def setLastPublishedShikimoriNewsTime(session, time):
    x = session.query(GlobalSettings).get(0)
    try:
        x.shikinewstime = time
        session.commit()
        # session.close()
        return "Success"
    except Exception as e:
        return f"Error: {e}"
