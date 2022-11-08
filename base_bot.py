import nextcord
from nextcord.ext import commands, tasks
from nextcord.ext.commands import CommandNotFound

from typing import Optional, Union, Any
import logging
import traceback
from sys import stdout

from modules.database import Database


class Bot(commands.Bot):
    def __init__(
        self,
        cogs_list: list[str],
        bot_settings: dict,
        bot_type: str = "BOT",
        database: Optional[Database] = None,
        debug: bool = False,
    ):
        super().__init__(help_command=None, intents=nextcord.Intents.all())

        self.cogs_list: list[str] = cogs_list
        self.bot_type = bot_type

        self.database = database

        self.current_status: str = "game"

        self.settings: dict = bot_settings
        self.command_prefix = self.command_prefixes
        self.prefixes: dict = {}

        self.logger: logging.Logger = logging.getLogger("milkbot")
        self.logger.setLevel(logging.INFO)

        self.FORMATTER = logging.Formatter(
            fmt=f"[%(asctime)s: %(levelname)s] [{bot_type}] %(message)s"
        )

        self.consoleHandler = logging.StreamHandler(stream=stdout)
        self.consoleHandler.setFormatter(self.FORMATTER)
        self.consoleHandler.setLevel(logging.INFO)

        self.logger.handlers = [self.consoleHandler]

        self.debug = debug

    def command_prefixes(self, bot, message: Union[nextcord.Message, str]) -> str:
        try:
            if isinstance(message, nextcord.Message):
                return self.prefixes[message.guild.id]
            elif isinstance(message, str):
                return self.prefixes[message]
            else:
                return "="
        except:
            return "="

    @tasks.loop(minutes=1)
    async def get_prefixes(self) -> None:
        self.prefixes: dict = self.database.get_all_prefixes()

    @tasks.loop(seconds=15)
    async def status_changer(self) -> None:
        match self.current_status:
            case "watching":
                await self.change_presence(
                    status=nextcord.Status.online,
                    activity=nextcord.Activity(
                        type=nextcord.ActivityType.playing, name="=help"
                    ),
                )
                self.current_status = "game"
            case "game":
                await self.change_presence(
                    status=nextcord.Status.online,
                    activity=nextcord.Activity(
                        type=nextcord.ActivityType.watching, name="на котиков."
                    ),
                )
                self.current_status = "watching"

    async def on_command_error(self, ctx: nextcord.ext.commands.Context, error):
        if isinstance(error, CommandNotFound):
            return
        else:
            exception_str = (
                (
                    f"When calling the command {ctx.command.name} by the user {ctx.author}, an error occurred."
                    if ctx.command is not None and ctx.author is not None
                    else ""
                )
                + (
                    f"When calling the command {ctx.command.name}, an error occurred."
                    if ctx.command is not None and ctx.author is None
                    else ""
                )
                + "\n"
                + "\n".join(traceback.format_exception(error))
            )
            self.logger.error(exception_str + "\n")
            try:
                owner: nextcord.User = await self.fetch_user(
                    self.settings.get("owner_id", None)
                )
                await owner.send(exception_str)
                self.logger.debug(f"Traceback have been sended to user. ID: {owner.id}")
            except:
                self.logger.debug(
                    f"Error was ocured when sending traceback to user. ID: {self.settings.get('owner_id', None)}"
                )

    async def on_message(self, message: nextcord.Message):
        if message.guild is None:
            return

        if self.debug:
            message_context: nextcord.ext.commands.Context = await self.get_context(
                message
            )
            if message_context.valid:
                self.logger.debug(
                    f"{message.author} ({message.author.id}) called command {message_context.command.name}"
                )

        await self.process_commands(message)

    async def on_ready(self):
        self.status_changer.start()
        self.get_prefixes.start()
        self.logger.info(f"Loggined as {self.user.name}")

    def run(self, *args: Any, **kwargs: Any) -> None:
        self.logger.info("Try to start")
        if self.debug:
            self.logger.setLevel(logging.DEBUG)
            self.consoleHandler.setLevel(logging.DEBUG)
            self.logger.debug("Debug mode enabled")

        if not self.cogs_list:
            raise UnboundLocalError("Cog's names list not found")
        if self.settings == {}:
            raise UnboundLocalError("Bot configuration not found")
        if self.database is None:
            try:
                self.database = Database(uri=self.settings["db_url"], bot=self)
                self.database.reconnect.start()
            except:
                raise UnboundLocalError("Database Subsystem not found")

        self.cogs_list.sort()
        self.logger.debug("Cog's names list sorted")
        self.logger.debug(f"Cog's names list: {self.cogs_list}")

        for cog_name in self.cogs_list:
            try:
                self.load_extension(cog_name)
                self.logger.info(f"Successfully loaded cog {cog_name}")
            except Exception as error:
                self.logger.error(
                    "Cog error: " + "\n".join(traceback.format_exception(error)) + "\n"
                )

        if not self.cogs:
            raise UnboundLocalError("No one cog didn't be loaded")
        self.logger.debug("Trying to autorize")
        self.logger.debug(f"Token: {self.settings['token']}")

        try:
            super().run(self.settings["token"])
        except Exception as error:
            self.logger.critical(
                "Autorization Error: " + "\n".join(traceback.format_exception(error))
            )
            raise error
