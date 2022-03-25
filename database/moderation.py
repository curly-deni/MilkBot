from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from datetime import datetime

from .db_classes import getTextMutesClass, getVoiceMutesClass


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


def getTextMutes(engine, guildid):
    # session = getSession(engine)
    x = getTextMutesBySession(session, guildid)
    # session.close()
    return x


def getTextMutesBySession(session, guildid):
    TextMute = getTextMutesClass(guildid)
    x = session.query(TextMute).filter(TextMute.time_stop < datetime.now())
    return x


def getVoiceMutes(session, guildid):
    # session = getSession(engine)
    VoiceMutes = getVoiceMutesClass(guildid)
    x = session.query(VoiceMutes).filter(VoiceMutes.time_stop < datetime.now())
    session.close()
    return x


def delTextElement(session, guildid, x):
    # session = getSession(engine)
    TextMutes = getTextMutesClass(guildid)
    session.query(TextMutes).filter(TextMutes.uid == x.uid).delete()
    session.commit()
    # session.close()


def delVoiceElement(session, guildid, x):
    # session = getSession(engine)
    VoiceMutes = getVoiceMutesClass(guildid)
    session.query(VoiceMutes).filter(VoiceMutes.uid == x.uid).delete()
    session.commit()
    # session.close()


def addTextMutes(session, x):
    # session = getSession(engine)
    try:
        session.add(x)
        session.commit()
        # session.close()
        return "pass"
    except Exception as e:
        return str(e)


def addVoiceMutes(session, x):
    # session = getSession(engine)
    try:
        session.add(x)
        session.commit()
        # session.close()
        return "pass"
    except Exception as e:
        return str(e)
