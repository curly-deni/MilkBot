from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from .db_classes import getVoiceSettingsClass


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


def getInfo(session, guildid, useruid):
    VoiceSettings = getVoiceSettingsClass(guildid)
    if session.query(VoiceSettings).get(useruid) == None:
        addInfo(session, guildid, useruid)
    return session.query(VoiceSettings).get(useruid)


def addInfo(session, guildid, useruid):
    session.add(getVoiceSettingsClass(guildid)(useruid=useruid, bitrate=64000))
    session.commit()


def setName(session, guildid, useruid, name):
    try:
        x = getInfo(session, guildid, useruid)
        x.name = name
        session.commit()
    except Exception as e:
        print(e)


def setMaxUser(session, guildid, useruid, max):
    try:
        x = getInfo(session, guildid, useruid)
        x.maxuser = max
        session.commit()
    except Exception as e:
        print(e)


def setBitrate(session, guildid, useruid, bitrate):
    try:
        x = getInfo(session, guildid, useruid)
        x.bitrate = bitrate
        session.commit()
    except Exception as e:
        print(e)


def addBanned(session, guildid, useruid, uidx):
    try:
        x = getInfo(session, guildid, useruid)
        if x.banned != None:
            x.banned = str(x.banned) + f"{uidx},"
        else:
            x.banned = f"{uidx},"
        session.commit()
    except Exception as e:
        print(e)


def delBanned(session, guildid, useruid, uidx):
    try:
        x = getInfo(session, guildid, useruid)
        if x.banned != None:
            g = x.banned.split(",")
            g.remove(str(uidx))
            x.banned = (",").join(g)
            session.commit()
    except Exception as e:
        print(e)


def addOpened(session, guildid, useruid, uidx):
    try:
        x = getInfo(session, guildid, useruid)
        if x.opened != None:
            x.opened = str(x.opened) + f"{uidx},"
        else:
            x.opened = f"{uidx},"
        session.commit()
    except Exception as e:
        print(e)


def delOpened(session, guildid, useruid, uidx):
    try:
        x = getInfo(session, guildid, useruid)
        if x.opened != None:
            g = x.opened.split(",")
            g.remove(str(uidx))
            x.opened = (",").join(g)
            session.commit()
    except Exception as e:
        print(e)


def addMuted(session, guildid, useruid, uidx):
    try:
        x = getInfo(session, guildid, useruid)
        if x.muted != None:
            x.muted = str(x.muted) + f"{uidx},"
        else:
            x.muted = f"{uidx},"
        session.commit()
    except Exception as e:
        print(e)


def delMuted(session, guildid, useruid, uidx):
    try:
        x = getInfo(session, guildid, useruid)
        if x.muted != None:
            g = x.muted.split(",")
            g.remove(str(uidx))
            x.muted = (",").join(g)
            session.commit()
    except Exception as e:
        print(e)


def setOpen(session, guildid, useruid, open):
    try:
        x = getInfo(session, guildid, useruid)
        x.open = open
        session.commit()
    except Exception as e:
        print(e)


def setText(session, guildid, useruid, text):
    try:
        x = getInfo(session, guildid, useruid)
        x.text = text
        session.commit()
    except Exception as e:
        print(e)


def setVisible(session, guildid, useruid, visible):
    try:
        x = getInfo(session, guildid, useruid)
        x.visible = visible
        session.commit()
    except Exception as e:
        print(e)
