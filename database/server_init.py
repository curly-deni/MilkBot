from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, BigInteger, TIMESTAMP, Boolean
from sqlalchemy import MetaData
from sqlalchemy.orm import scoped_session, sessionmaker

from .globalsettings import getEmbMasterTable, getArtMasterTable, getAstralMasterTable
from .serversettings import setEmbTable, setArtTable, setAstralTable, getInfo
from .embed import createEmbedTable, gcAuthorize
from .art import createArtTable
from .astral import createAstralTable


def initServer(uri, guildid):
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

    shikimori = Table(
        f"shikimori-{guildid}",
        meta,
        Column("id", BigInteger, primary_key=True),
        Column("sid", BigInteger),
    )

    tmutes = Table(
        f"textmutes-{guildid}",
        meta,
        Column("uid", BigInteger, primary_key=True),
        Column("reason", String),
        Column("created", BigInteger),
        Column("time_start", TIMESTAMP),
        Column("time_stop", TIMESTAMP),
    )

    vmutes = Table(
        f"voicemutes-{guildid}",
        meta,
        Column("uid", BigInteger, primary_key=True),
        Column("reason", String),
        Column("created", BigInteger),
        Column("time_start", TIMESTAMP),
        Column("time_stop", TIMESTAMP),
    )

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

    voicechannels = Table(
        f"voicechannels-{guildid}",
        meta,
        Column("vcuid", BigInteger, primary_key=True),
        Column("txuid", BigInteger),
        Column("owuid", BigInteger),
    )

    engine = create_engine(uri)
    meta.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()
    gc = gcAuthorize()

    getInfo(session, int(guildid))

    setEmbTable(
        session, int(guildid), createEmbedTable(gc, guildid, getEmbMasterTable(session))
    )

    setArtTable(
        session, int(guildid), createArtTable(gc, guildid, getArtMasterTable(session))
    )

    try:
        setAstralTable(
            session,
            int(guildid),
            createAstralTable(gc, guildid, getAstralMasterTable(session)),
        )
    except:
        pass

    session.close()
