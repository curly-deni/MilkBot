import nextcord
from nextcord.ext import commands, tasks
from nextcord.ext.commands import CommandNotFound
from settings import settings, adminRoles

prefixes = {}

# database
import database.serversettings as serversettings
import database.server_init as server_init
import database.globalsettings as globalsettings
from database.connector import connectToDatabase

uri = settings["StatUri"]

# for logs
from datetime import datetime
import asyncio


def prefix_func(bot, message):
    global prefixes
    if isinstance(message, nextcord.Message):
        try:
            return prefixes[message.guild.id]
        except:
            return "="
    else:
        try:
            return prefixes[message]
        except:
            return "="


class MilkBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=prefix_func,
            help_command=None,
            intents=nextcord.Intents.all(),
        )
        self.databaseSession = None
        self.reconnect.start()

    @tasks.loop(seconds=60)
    async def reconnect(self):
        self.databaseSession = connectToDatabase(uri, self.databaseSession)

    @tasks.loop(minutes=1)  # repeat after every 60 seconds
    async def getPrefixes(self):
        global prefixes

        prefixes = serversettings.getAllPrefixes(self.databaseSession)


bot = MilkBot()


@bot.event
async def on_message(message):
    await bot.process_commands(message)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    raise error


@bot.event
async def on_ready():
    try:
        bot.getPrefixes.start()
    except:
        pass

    print(f"{bot.user.name} ready!")
    game = nextcord.Game("=help")
    await bot.change_presence(status=nextcord.Status.online, activity=game)


@bot.command(pass_context=True, aliases=[f"статус"])
@commands.dm_only()
@commands.is_owner()
async def setstatus(ctx, *, status):
    game = nextcord.Game(status)
    await bot.change_presence(status=nextcord.Status.online, activity=game)


@bot.command(pass_context=True)
async def ping(ctx):
    await ctx.send(f"Server answer. Pong! {round(bot.latency, 1)}")


cogs = [
    "cogs.astral.functions",
]

if __name__ == "__main__":
    print("""MilkBot v2.2.4
Developed by Dan_Mi
""")

    print(f"""System Information:
Token: {settings["token"]}
Database link: {settings["StatUri"]}
""")

    print("Loading cogs\n")

    for cog in cogs:
        print(f"Now loading {cog}")
        try:
            bot.load_extension(cog)
        except Exception as e:
            print(f"Cog {cog} raise Exception: {e}")
            pass

    print("Start Bot")
    bot.run(settings["token"])
