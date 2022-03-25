from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from .db_classes import GlobalSettings


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
