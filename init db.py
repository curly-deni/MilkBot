from sqlalchemy import create_engine
from sqlalchemy import inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, BigInteger, TIMESTAMP, Boolean
from sqlalchemy import MetaData
from sqlalchemy.orm import scoped_session, sessionmaker
from settings import production_settings as settings


def createServerSettingsTable(uri):
    meta = MetaData()

    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)

    serversettings = Table(
        f"serversettings",
        meta,
        Column("uid", BigInteger, primary_key=True),
        Column("prefix", String),
        Column("userroles", String),
        Column("adminroles", String),
        Column("embtable", String),
        Column("astralspr", String),
        Column("astralscr", String),
        Column("astralspr", String),
        Column("voicegenerator", BigInteger),
        Column("voicecategory", BigInteger),
        Column("voicemessage", BigInteger),
        Column("horo", Boolean),
        Column("hororole", BigInteger),
        Column("horochannel", BigInteger),
        Column("shikinews", Boolean),
        Column("shikinewschannel", BigInteger),
        Column("shikirelease", Boolean),
        Column("shikireleasechannel", BigInteger),
    )

    engine = create_engine(uri)
    meta.create_all(engine)


def createGlobalSettingsTable(uri):
    meta = MetaData()

    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)

    gs = Table(
        f"globalsettings",
        meta,
        Column("id", Integer, primary_key=True),
        Column("mprefix", String),
        Column("astraltable", String),
        Column("embtable", String),
        Column("arttable", String),
        Column("shikinewstime", TIMESTAMP),
    )

    engine = create_engine(uri)
    meta.create_all(engine)


if __name__ == "__main__":
    createServerSettingsTable(settings["StatUri"])
    createServerSettingsTable(settings["StatUri"])
