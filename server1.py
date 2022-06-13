import datetime

import nextcord
from nextcord.ext import commands, tasks, ipc
from nextcord.ext.commands import CommandNotFound
import asyncio
from tables import Tables
from database import Database
from typing import Union
import argparse
import logging
import sys
import asyncio

cogs = [
    "cogs.help.functions",
    "cogs.rp.functions",
    "cogs.fakeastral.functions",
    "cogs.setup.functions",
    "cogs.genshin.functions",
    "cogs.kisik_rp.functions",
    "cogs.kisik_moderation.functions",
    "cogs.moderation.functions",
    "cogs.kisik_mailing.functions",
    "cogs.mailing.functions",
    "cogs.stats.functions",
    "cogs.statcount.functions",
    "cogs.voice.functions",
    "cogs.shikimori.functions",
    "cogs.quiz.functions",
    "cogs.ipc.functions",
]


class MilkBot3(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.database: Database = None
        self.command_prefix = self.prefix_func
        self.tables: Tables = Tables(self)
        self.current_status = "game"

        self.settings: dict = {}
        self.prefixes: dict = {}

        self.logger: logging.Logger = logging.getLogger("logger")
        self.logger.setLevel(logging.INFO)

        self.FORMATTER = logging.Formatter(
            fmt="[%(asctime)s: %(levelname)s] %(message)s"
        )

        dt = datetime.datetime.now()

        self.fileHandler = logging.FileHandler(
            f"./logs/{dt.day}-{dt.month}-{dt.year}-server1.log"
        )
        self.fileHandler.setFormatter(self.FORMATTER)
        self.fileHandler.setLevel(logging.INFO)

        self.consoleHandler = logging.StreamHandler(stream=sys.stdout)
        self.consoleHandler.setFormatter(self.FORMATTER)
        self.consoleHandler.setLevel(logging.INFO)

        self.logger.handlers = [self.fileHandler, self.consoleHandler]

        self.debug: bool = False

    def setup_ipc(self) -> None:
        self.ipc = ipc.Server(self, port=8765, secret_key=self.settings["ipc_key"])

    async def on_ipc_ready(self):
        self.logger.info("IPC is ready")

    # async def on_ipc_error(self, endpoint, error):
    #     self.logger.error(endpoint, "raised", error)

    @tasks.loop(hours=24)
    async def change_log_file(self):
        self.logger.handlers.remove(self.fileHandler)

        dt = datetime.datetime.now()

        self.fileHandler = logging.FileHandler(
            f"./logs/{dt.day}-{dt.month}-{dt.year}-server1.log"
        )
        self.fileHandler.setFormatter(self.FORMATTER)
        self.fileHandler.setLevel(logging.INFO)

        self.logger.handlers.append(self.fileHandler)

    @change_log_file.before_loop
    async def before_change_log_file(self):
        hour = 0
        minute = 1
        await self.wait_until_ready()
        now = datetime.datetime.now()
        future = datetime.datetime(now.year, now.month, now.day, hour, minute)
        if now.hour >= hour and now.minute > minute:
            future += datetime.timedelta(days=1)
        await asyncio.sleep((future - now).seconds)

    def prefix_func(self, bot, message: Union[nextcord.Message, str]) -> str:
        if isinstance(message, nextcord.Message):
            try:
                return self.prefixes[message.guild.id]
            except:
                return "="
        elif isinstance(message, str):
            try:
                return self.prefixes[message]
            except:
                return "="
        else:
            return "="

    @tasks.loop(minutes=1)
    async def get_prefixes(self) -> None:
        self.prefixes = self.database.get_all_prefixes()

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


bot = MilkBot3(
    help_command=None,
    intents=nextcord.Intents.all(),
)


@bot.event
async def on_message(message):
    if message.content.find(str(bot.user.id)) != -1:
        prefix = bot.database.get_guild_prefix(message.guild.id)
        emb = nextcord.Embed(
            title=f"""Привет!
Я {bot.user.name}! Мой префикс на этом сервере - {prefix}.
Ознакомиться с моими возможностямит можно по команде {prefix}help.
"""
        )
        await message.reply(embed=emb)
    else:
        await bot.process_commands(message)


@bot.event
async def on_ready():
    bot.tables.reconnect.start()
    bot.get_prefixes.start()
    bot.change_log_file.start()
    bot.status_changer.start()
    bot.logger.info(f"{bot.user.name} started")


@bot.command()
@commands.is_owner()
async def load(ctx, *, module):
    try:
        bot.load_extension(f"cogs.{module}.functions")
        return await ctx.send(f"cogs.{module}.functions loaded successful!")
    except Exception:
        bot.logger.exception(str(Exception))
        return await ctx.send(str(Exception))


@bot.command()
@commands.is_owner()
async def unload(ctx, *, module):
    try:
        bot.unload_extension(f"cogs.{module}.functions")
        return await ctx.send(f"cogs.{module}.functions loaded successful!")
    except Exception:
        return await ctx.send(str(Exception))


@bot.command()
@commands.is_owner()
async def reload(ctx, *, module):
    try:
        bot.reload_extension(f"cogs.{module}.functions")
        return await ctx.send(f"cogs.{module}.functions loaded successful!")
    except Exception:
        return await ctx.send(str(Exception))


@bot.command()
async def ping(ctx):
    await ctx.send(f"Server answer. Pong! {round(bot.latency, 1)}")


if __name__ == "__main__":
    cogs.sort()

    parser = argparse.ArgumentParser()
    parser.add_argument("--dev")
    args = parser.parse_args()

    bot.logger.info("Bot version: 3.3.2")

    if args.dev != "on":
        from settings import production_settings

        bot.settings = production_settings

    else:
        bot.debug = True
        from settings import developer_settings

        bot.settings = developer_settings

        bot.logger.setLevel(logging.DEBUG)
        bot.fileHandler.setLevel(logging.DEBUG)
        bot.consoleHandler.setLevel(logging.DEBUG)
        bot.logger.debug("Debug mode enabled")

    bot.logger.info(f"Token: {bot.settings['token']}")
    bot.logger.info(f"Database link: {bot.settings['DatabaseUri']}")

    bot.setup_ipc()

    try:
        bot.database = Database(uri=bot.settings["DatabaseUri"], bot=bot)
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

    bot.ipc.start()

    try:
        bot.run(bot.settings["token"])
    except Exception as e:
        bot.logger.critical(f"Bot login error: {e}")
        exit()
