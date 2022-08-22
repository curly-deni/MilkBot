import nextcord
from nextcord.ext import commands, tasks
from nextcord.ext.commands import CommandNotFound

from typing import Optional, Union
import argparse
import logging
import sys
from json import load

from modules.database import Database
from modules.tables import Tables

cogs = [
    "cogs.fakeastral.functions",
    "cogs.genshin_stat.functions",
    "cogs.guild_stat.functions",
    "cogs.help.functions",
    "cogs.ipc_server.functions",
    "cogs.kisik_mailing.functions",
    "cogs.kisik_moderation.functions",
    "cogs.mailing.functions",
    "cogs.moderation.functions",
    "cogs.quiz.functions",
    "cogs.rp.functions",
    "cogs.setup.functions",
    "cogs.shibu_room.functions",
    "cogs.shikimori_mailing.functions",
    "cogs.shikimori_stat.functions",
    "cogs.stat_counter.functions",
    "cogs.terms_of_usage.functions",
    "cogs.voice.functions",
]


class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bot_type: str = "bot"
        self.version: str = "4.0"

        self.database: Optional[Database] = None
        self.tables: Tables = Tables(self)

        self.current_status: str = "game"
        self.command_prefix = self.prefix_func

        self.settings: dict = {}
        self.prefixes: dict = {}

        self.logger: logging.Logger = logging.getLogger("bot-logger")
        self.logger.setLevel(logging.INFO)

        self.FORMATTER = logging.Formatter(
            fmt=f"{self.bot_type}-[%(asctime)s: %(levelname)s] %(message)s"
        )

        self.consoleHandler = logging.StreamHandler(stream=sys.stdout)
        self.consoleHandler.setFormatter(self.FORMATTER)
        self.consoleHandler.setLevel(logging.INFO)

        self.logger.handlers = [self.consoleHandler]

        self.debug: bool = False
        self.attached_guild: Optional[int] = None

    def prefix_func(self, bot, message: Union[nextcord.Message, str]) -> str:
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
        match bot.current_status:
            case "watching":
                await bot.change_presence(
                    status=nextcord.Status.online,
                    activity=nextcord.Activity(
                        type=nextcord.ActivityType.playing, name="=help"
                    ),
                )
                self.current_status = "game"
            case "game":
                await bot.change_presence(
                    status=nextcord.Status.online,
                    activity=nextcord.Activity(
                        type=nextcord.ActivityType.watching, name="на котиков."
                    ),
                )
                self.current_status = "watching"


bot = Bot(
    help_command=None,
    intents=nextcord.Intents.all(),
)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    else:
        bot.logger.error(str(error))
        raise error


@bot.event
async def on_message(message):
    if message.guild is None:
        return

    if bot.attached_guild is not None and bot.attached_guild != message.guild.id:
        return

    if bot.bot_type == "helper" and message.content.find("help") != -1:
        await bot.process_commands(message)

    if bot.bot_type != "helper":
        await bot.process_commands(message)


@bot.event
async def on_ready():
    if bot.bot_type != "helper":
        bot.status_changer.start()
        bot.tables.reconnect.start()
        bot.get_prefixes.start()
    bot.logger.info(f"Loggined as {bot.user.name}")


if __name__ == "__main__":

    cogs.sort()

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d", "--debug", help="enable debug and dev settings", action="store_true"
    )
    parser.add_argument("-g", "--guild_id", type=int, help="attach bot to guild")
    parser.add_argument("-c", "--config", type=str, help="config name in configs path")
    args = parser.parse_args()

    if args.guild_id is not None:
        if isinstance(args.guild_id, int) or args.guild_id.isdigit():
            bot.attached_guild = int(args.guild_id)
            bot.logger.info(f"Bot attached to guild. ID: {bot.attached_guild}")

    if args.config is not None:
        try:
            with open(f"./configs/{args.config}.json") as f:
                bot.settings = load(f)
        except:
            bot.logger.error("Unable to load config. Loads current")
            with open("./configs/current.json") as f:
                bot.settings = load(f)
    else:
        if not args.debug:
            with open("./configs/current.json") as f:
                bot.settings = load(f)

        else:
            with open("./configs/dev.json") as f:
                bot.settings = load(f)

    if args.debug:
        bot.debug = True

        bot.logger.setLevel(logging.DEBUG)
        bot.consoleHandler.setLevel(logging.DEBUG)
        bot.logger.debug("Debug mode enabled")

    bot.logger.info(f"Token: {bot.settings['token']}")
    bot.logger.info(f"Database link: {bot.settings['db_url']}")

    try:
        bot.database = Database(uri=bot.settings["db_url"], bot=bot)
        bot.database.reconnect.start()
    except Exception as e:
        bot.logger.critical(f"Database connect error: {e}")
        exit()

    for cog in cogs:
        try:
            bot.load_extension(cog)
            bot.logger.info(f"Loaded {cog}")
        except Exception as e:
            bot.logger.error(f"Cog error: {e}")

    bot.logger.info("Trying to login")

    try:
        bot.run(bot.settings["token"])
    except Exception as e:
        bot.logger.critical(f"Bot login error: {e}")
        exit()
