import asyncio
from datetime import datetime
from functools import wraps
from os import path, walk, curdir
from typing import Optional

# from cachetools import TTLCache
from nextcord import Intents, Message
from nextcord.ext import tasks
from nextcord.ext.commands import AutoShardedBot, Bot as NBot
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession

from framecho.logger import Logger
from .md import ModuleLoader

loader = ModuleLoader("./")
ext = []

for md in loader.modules.values():
    ext.extend(md.ext.values())

from config import *

BotBase = AutoShardedBot if IS_SHARED else NBot

__all__ = ["Bot"]


class Bot(BotBase):
    _instance = None
    _logger: Logger = None
    _is_shared = IS_SHARED

    _owner_id = -1
    _permission_checkers = {}

    @staticmethod
    def add_permission_checker(key: Optional[str] = None):
        def wrapper(func):
            @wraps(func)
            def wrapped(*args, **kwargs):
                return func(*args, **kwargs)

            Bot._permission_checkers[key or func.__name__] = func
            return wrapped

        return wrapper

    @property
    def permission_checkers(self):
        return Bot._permission_checkers

    @property
    def logger(self):
        return self._logger

    @property
    def is_shared(self):
        return self._is_shared

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, *args, **kwargs):
        if hasattr(self, "_initialized"):
            return

        super().__init__(intents=Intents.all(), *args, **kwargs)
        self.command_prefix = STANDARD_PREFIX

        self._logger = Logger()
        self._prefixes_cache = {}

        self.__db_engine = create_async_engine(url=DB_SETTINGS.get_url())
        self._session_maker = async_sessionmaker(
            self.__db_engine, expire_on_commit=False
        )

        self._system_session_opened: bool = False
        self._system_session: Optional[AsyncSession] = None

        self._initialized = True
        self._loaded_once = False

    async def on_ready(self):
        await self._process_ready()
        await self._process_ready_once()
        self._logger.info(f"Logged in as {self.user}")

    async def _process_ready(self):
        pass

    async def _process_ready_once(self):
        if self._loaded_once:
            return

        await self._get_owner_id()

        self._loaded_once = True

    async def _get_owner_id(self):
        await self.application_info()

    # async def get_command_prefixes_from_db(self):
    #     async with self.session_maker() as session:
    #          query = select(GuildPrefix).

    @tasks.loop(seconds=30)
    async def _system_session_loop(self):
        async def make_session():
            self._system_session_opened = False
            if self._system_session is not None:
                await self._system_session.close()

            self._system_session = await self.session_maker().__aenter__()
            self._system_session_opened = True

        tries = 0
        while True:
            try:
                await make_session()
                break
            except Exception as e:
                self._logger.error("Error while creating system session", e)
                tries += 1
                if tries > 3:
                    break

    async def get_system_session(self):
        while not self._system_session_opened:
            await asyncio.sleep(0.1)
        return self._system_session

    @_system_session_loop.before_loop
    async def _before_system_session_loop(self):
        await self.wait_until_ready()

    @property
    def session_maker(self):
        return self._session_maker

    def process_command_prefix(self, message: Message) -> str:
        if isinstance(message, Message):
            guild_id = message.guild.id
        elif isinstance(message, int):
            guild_id = message
        elif isinstance(message, str) and message.isnumeric():
            guild_id = int(message)

        else:
            return STANDARD_PREFIX

        if guild_id in self.__prefixes_cache:
            return self.__prefixes_cache[guild_id]

        return STANDARD_PREFIX

    @staticmethod
    def _print_startup_message():
        print("Framecho - Enhanced Discord Framework")
        print(f"Bot Toolkit (BTK) (v0.1)")
        print(
            f"Copyright (c) 2025-{datetime.now().year} curly_deni (danila@dan-mi.ru)\n"
        )
        if STARTUP_MESSAGE:
            print("----------\n" + STARTUP_MESSAGE + "\n----------\n")

    def _initialize_logger(self):
        self._logger.set_debug_level() if DEBUG else self._logger.set_info_level()
        (
            self._logger.enable_file_logging()
            if FILE_LOGGING
            else self._logger.disable_file_logging()
        )
        self._logger.info("Logger initialized")

    def _autoload_cogs_from_dir(self, base_path, prefix):
        total, loaded, failed = 0, 0, 0
        target_path = path.join(path.abspath(curdir), base_path)

        self._logger.info(f'Autoloading cogs from "{base_path}"')

        for module in next(walk(target_path), (None, None, []))[2]:
            if module == "__pycache__" or module.endswith("~"):
                continue
            try:
                self.load_extension(f"{prefix}.{module}".replace(".py", ""))
                self._logger.info(f'Loaded cog "{module}"')
                loaded += 1
            except Exception as e:
                self._logger.error(f'Failed to load cog "{module}"', e)
                failed += 1
            total += 1

        self._logger.info(
            f"Autoloaded {total} cogs: {loaded} successfully, {failed} failed"
        )

    def _load_cogs_from_list(self, cogs_list):
        total, loaded, failed = 0, 0, 0

        for cog in cogs_list:
            try:
                self.load_extension(cog)
                self._logger.info(f'Loaded cog "{cog}"')
                loaded += 1
            except Exception as e:
                self._logger.error(f'Failed to load cog "{cog}"', e)
                failed += 1
            total += 1

        self._logger.info(
            f"Loaded {total} cogs: {loaded} successfully, {failed} failed"
        )

    def _load_cogs_from_modules(self):
        for _md in loader.modules.values():
            if not _md.cogs:
                continue

            self._logger.info(f"Loading cogs from module {_md.name}")
            self._load_cogs_from_list(_md.cogs)

    def run(self, token):
        self._print_startup_message()
        self._initialize_logger()
        self._load_cogs_from_modules()
        # self._autoload_cogs()
        super().run(token)
