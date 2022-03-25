from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, BigInteger, TIMESTAMP, Boolean

Base = declarative_base()


def getGenshinClass(guildid):
    Base = declarative_base()

    class Genshin(Base):
        __tablename__ = f"genshin-{guildid}"
        __table_args__ = {"extend_existing": True}

        uid = Column(BigInteger, primary_key=True)
        mihoyouid = Column(BigInteger)
        genshinuid = Column(BigInteger)

        genshinname = Column(String)
        discordname = Column(String)
        ar = Column(Integer)
        background = Column(String)

        color_stat = Column(String)
        color_name = Column(String)
        color_titles = Column(String)

    return Genshin


def getShikimoriClass(guildid):
    Base = declarative_base()

    class Shikimori(Base):
        __tablename__ = f"shikimori-{guildid}"
        __table_args__ = {"extend_existing": True}

        id = Column(BigInteger, primary_key=True)
        sid = Column(BigInteger)

    return Shikimori


def getVoiceMutesClass(guildid):
    Base = declarative_base()

    class VoiceMutes(Base):
        __tablename__ = f"voicemutes-{guildid}"
        __table_args__ = {"extend_existing": True}

        uid = Column(BigInteger, primary_key=True)

        reason = Column(String)
        created = Column(BigInteger)
        time_start = Column(TIMESTAMP)
        time_stop = Column(TIMESTAMP)

    return VoiceMutes


def getTextMutesClass(guildid):
    Base = declarative_base()

    class TextMutes(Base):

        __tablename__ = f"textmutes-{guildid}"
        __table_args__ = {"extend_existing": True}

        uid = Column(BigInteger, primary_key=True)

        reason = Column(String)
        created = Column(BigInteger)
        time_start = Column(TIMESTAMP)
        time_stop = Column(TIMESTAMP)

    return TextMutes


def getStatClass(guildid):
    Base = declarative_base()

    class Stat(Base):
        __tablename__ = f"stat-{guildid}"
        __table_args__ = {"extend_existing": True}

        uid = Column(BigInteger, primary_key=True)

        background = Column(String)
        quotex = Column(String)
        color = Column(String)
        coin = Column(Integer)
        allvoicetime = Column(BigInteger)

        voiceconn = Column(TIMESTAMP)
        xp = Column(BigInteger)
        lvl = Column(Integer)
        cookie = Column(Integer)

    return Stat


def getVoiceSettingsClass(guildid):
    Base = declarative_base()

    class VoiceSettings(Base):
        __tablename__ = f"voicesettings-{guildid}"
        __table_args__ = {"extend_existing": True}

        useruid = Column(BigInteger, primary_key=True)

        bitrate = Column(Integer)
        maxuser = Column(Integer)

        name = Column(String)
        banned = Column(String)
        muted = Column(String)
        opened = Column(String)

        open = Column(Boolean)
        visible = Column(Boolean)
        text = Column(Boolean)

    return VoiceSettings


def getVoiceChannelsClass(guildid):
    Base = declarative_base()

    class VoiceChannels(Base):
        __tablename__ = f"voicechannels-{guildid}"
        __table_args__ = {"extend_existing": True}

        vcuid = Column(BigInteger, primary_key=True)
        txuid = Column(BigInteger)
        owuid = Column(BigInteger)

    return VoiceChannels


class GlobalSettings(Base):
    __tablename__ = "globalsettings"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True)
    mprefix = Column(String)

    astraltable = Column(String)
    embtable = Column(String)
    arttable = Column(String)


class ServerSettings(Base):
    __tablename__ = "serversettings"
    __table_args__ = {"extend_existing": True}

    uid = Column(BigInteger, primary_key=True)
    prefix = Column(String)

    userroles = Column(String)
    adminroles = Column(String)

    embtable = Column(String)
    astralspr = Column(String)
    astralscr = Column(String)
    artspr = Column(String)

    voicegenerator = Column(BigInteger)
    voicecategory = Column(BigInteger)
