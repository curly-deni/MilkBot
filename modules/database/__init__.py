import sqlalchemy.engine
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from nextcord.ext import tasks
from typing import Optional

from .bot_settings import BotSettingsDbMethods
from .guild_settings import GuildSettingsDbMethods
from .guild_stat import GuildStatisticDbMethods
from .shiki_prof import ShikimoriProfilesDbMethods
from .mutes import MutesDbMethods
from .voice import VoiceDbMethods
from .genshin_prof import GenshinProfilesDbMethods
from .table_classes import *


class Database(
    BotSettingsDbMethods,
    GuildSettingsDbMethods,
    GuildStatisticDbMethods,
    ShikimoriProfilesDbMethods,
    MutesDbMethods,
    VoiceDbMethods,
    GenshinProfilesDbMethods,
):
    def __init__(self, uri: str, bot=None):
        self.__uri = uri
        self.bot = bot

        self.__engine: Optional[sqlalchemy.engine.base.Engine] = None
        self.session: Optional[sqlalchemy.orm.session.Session] = None

    @tasks.loop(seconds=120)
    async def reconnect(self):
        if isinstance(self.__engine, sqlalchemy.engine.base.Engine):
            self.session.close()
            self.__engine.dispose()

        self.__engine: sqlalchemy.engine.Engine = create_engine(self.__uri)
        self.__engine.execute("ROLLBACK")

        self.session: sqlalchemy.orm.Session = sessionmaker(bind=self.__engine)()
