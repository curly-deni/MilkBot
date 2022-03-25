from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from .db_classes import getVoiceChannelsClass


def connectToDatabase(uri, session):
    if session != None:
        enginex = session.get_bind()
        session.close()
        enginex.dispose()

    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)

    engine = create_engine(uri)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def getInfo(session, guildid, vcuid):
    VoiceChannels = getVoiceChannelsClass(guildid)
    if session.query(VoiceChannels).get(vcuid) == None:
        addInfo(session, guildid, vcuid)
    return session.query(VoiceChannels).get(vcuid)


def addInfo(session, guildid, vcuid, txuid=None, owuid=None):
    session.add(getVoiceChannelsClass(guildid)(vcuid=vcuid, txuid=txuid, owuid=owuid))
    session.commit()


def delChannel(session, guildid, x):
    # session = getSession(engine)
    VoiceChannels = getVoiceChannelsClass(guildid)
    session.query(VoiceChannels).filter(VoiceChannels.vcuid == x.vcuid).delete()
    session.commit()
    # session.close()


def getTextChannelByUID(session, guildid, vcuid):
    return getInfo(session, guildid, vcuid).txuid


def getOwnerlByUID(session, guildid, vcuid):
    return getInfo(session, guildid, vcuid).owuid


def addTextChannelByUID(session, guildid, vcuid, txuid):
    x = getInfo(session, guildid, vcuid)
    try:
        x.txuid = txuid
        session.commit()
        return "Success"
    except Exception as e:
        return f"Error: {e}"
