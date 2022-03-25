from sqlalchemy import create_engine
from sqlalchemy import inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, BigInteger, TIMESTAMP, Boolean
from sqlalchemy import MetaData
from sqlalchemy.orm import scoped_session, sessionmaker


def createShikimoriTable(uri, guildid):
    meta = MetaData()

    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)

    shikimori = Table(
        f"shikimori-{guildid}",
        meta,
        Column("id", BigInteger, primary_key=True),
        Column("sid", BigInteger),
    )

    engine = create_engine(uri)
    meta.create_all(engine)


def createGenshinTable(uri, guildid):
    meta = MetaData()

    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)

    genshin = Table(
        f"genshin-{guildid}",
        meta,
        Column("uid", BigInteger, primary_key=True),
        Column("mihoyouid", BigInteger),
        Column("genshinuid", BigInteger),
        Column("genshinname", String),
        Column("discordname", String),
        Column("ar", Integer),
        Column("background", String),
        Column("color_stat", String),
        Column("color_name", String),
        Column("color_titles", String),
    )

    engine = create_engine(uri)
    meta.create_all(engine)


def createTMutesTable(uri, guildid):
    meta = MetaData()

    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)

    tmutes = Table(
        f"textmutes-{guildid}",
        meta,
        Column("uid", BigInteger, primary_key=True),
        Column("reason", String),
        Column("created", BigInteger),
        Column("time_start", TIMESTAMP),
        Column("time_stop", TIMESTAMP),
    )

    engine = create_engine(uri)
    meta.create_all(engine)


def createVMutesTable(uri, guildid):
    meta = MetaData()

    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)

    vmutes = Table(
        f"voicemutes-{guildid}",
        meta,
        Column("uid", BigInteger, primary_key=True),
        Column("reason", String),
        Column("created", BigInteger),
        Column("time_start", TIMESTAMP),
        Column("time_stop", TIMESTAMP),
    )

    engine = create_engine(uri)
    meta.create_all(engine)


def createStatTable(uri, guildid):
    meta = MetaData()

    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)

    stat = Table(
        f"stat-{guildid}",
        meta,
        Column("uid", BigInteger, primary_key=True),
        Column("background", String),
        Column("quotex", String),
        Column("color", String),
        Column("coin", Integer),
        Column("allvoicetime", BigInteger),
        Column("voiceconn", TIMESTAMP),
        Column("xp", BigInteger),
        Column("lvl", Integer),
        Column("cookie", Integer),
    )

    engine = create_engine(uri)
    meta.create_all(engine)


def createVoiceSettingsTable(uri, guildid):
    meta = MetaData()

    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)

    voicesettings = Table(
        f"voicesettings-{guildid}",
        meta,
        Column("useruid", BigInteger, primary_key=True),
        Column("bitrate", Integer),
        Column("maxuser", Integer),
        Column("name", String),
        Column("banned", String),
        Column("muted", String),
        Column("opened", String),
        Column("open", Boolean),
        Column("visible", Boolean),
        Column("text", Boolean),
    )

    engine = create_engine(uri)
    meta.create_all(engine)


def createVoiceChannelsTable(uri, guildid):
    meta = MetaData()

    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)

    voicechannels = Table(
        f"voicechannels-{guildid}",
        meta,
        Column("vcuid", BigInteger, primary_key=True),
        Column("txuid", BigInteger),
        Column("owuid", BigInteger),
    )

    engine = create_engine(uri)
    meta.create_all(engine)


def getTablesList(uri, tablename):

    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)

    engine = create_engine(uri)
    insp = inspect(engine)
    tables = insp.get_table_names()

    guilds = []
    for table in tables:
        if table.find(tablename) != -1:
            guilds.append(int(table.replace(f"{tablename}-", "")))

    return guilds


def createTables(uri, guilds, tablename):

    exguilds = getTablesList(uri, tablename)
    newguilds = list(set(guilds) - set(exguilds))

    for guild in newguilds:
        match tablename.lower():
            case "shikimori":
                createShikimoriTable(uri, guild)
            case "genshin":
                createGenshinTable(uri, guild)
            case "tmutes":
                createTMutesTable(uri, guild)
            case "vmutes":
                createVMutesTable(uri, guild)
            case "stat":
                createStatTable(uri, guild)
            case "voicesettings":
                createVoiceSettingsTable(uri, guild)
            case "voicechannels":
                createVoiceChannelsTable(uri, guild)
