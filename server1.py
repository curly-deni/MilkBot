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


# bot init


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
        global session

        self.databaseSession = connectToDatabase(uri, self.databaseSession)
        session = self.databaseSession


session = None
bot = MilkBot()


@tasks.loop(minutes=1)  # repeat after every 60 seconds
async def getPrefixes():
    global prefixes
    global session

    prefixes = serversettings.getAllPrefixes(session)


@bot.event
async def on_message(message):
    if message.content.find(f"{bot.user.id}") != -1:
        pr = serversettings.getPrefix(session, message.guild.id)
        emb = nextcord.Embed(title="Привет!")
        emb.add_field(
            name=f"Я {bot.user.name}!",
            value=f"Мой префикс на этом сервере - {pr}\nОзнакомиться с моими возможностями можно по команде **{pr}help**.",
        )
        await message.reply(embed=emb)
    else:
        await bot.process_commands(message)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    raise error


@bot.event
async def on_ready():
    getPrefixes.start()
    bot.load_extension("cogs.voice.functions")

    print("loaded")
    game = nextcord.Game("=help")
    await bot.change_presence(status=nextcord.Status.online, activity=game)


@bot.command(pass_context=True, aliases=[f"статус"])
@commands.dm_only()
@commands.is_owner()
async def setstatus(ctx, *args):
    e = (" ").join(args)
    game = nextcord.Game(e)
    await bot.change_presence(status=nextcord.Status.online, activity=game)


@bot.command(pass_context=True)
@commands.is_owner()
async def load(ctx, *args):
    try:
        e = "cogs." + (" ").join(args) + ".functions"
        bot.load_extension(e)
        ou = f"{e} loaded successful!"
        pass
    except Exception as f:
        ou = f"{e} error: {f}"
        pass
    await ctx.send(ou)


@bot.command(pass_context=True)
@commands.is_owner()
async def unload(ctx, *args):
    try:
        e = "cogs." + (" ").join(args) + ".functions"
        bot.unload_extension(e)
        ou = f"{e} unloaded successful!"
        pass
    except Exception as f:
        ou = f"{e} error: {f}"
        pass
    await ctx.send(ou)


@bot.command(pass_context=True)
async def ping(ctx):
    await ctx.send(f"Server answer. Pong! {round(bot.latency, 1)}")


cogs = [
    "cogs.help.functions",
    # "cogs.astral.functions",
    # "cogs.intreaction.functions",
    # "cogs.userreaction.functions",
    "cogs.moderation.functions",
    "cogs.milk.functions",
    "cogs.setup.functions",
    "cogs.rp.functions",
    "cogs.rp_nsfw.functions",
    # "cogs.arts.functions",
    "cogs.genshin.functions",
    "cogs.statcount.functions",
    "cogs.stats.functions",
    "cogs.shikimori.functions",
]

for cog in cogs:
    try:
        bot.load_extension(cog)
    except Exception as e:
        print(e)
        pass


bot.run(settings["token"])
