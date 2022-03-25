# This is executable for the first server of MilkBot

# for discord
import nextcord
from nextcord.ext import commands
from nextcord.ext.commands import CommandNotFound
from nextcord.ext import tasks
from settings import settings
from settings import adminRoles

prefixes = {}

# database
session = None
connected = False
import database.serversettings as serversettings
import database.server_init as server_init
import database.globalsettings as globalsettings

uri = settings["StatUri"]

# for logs
from datetime import datetime
import asyncio


def prefix_func(bot, message):
    global prefixes
    try:
        return prefixes[message.guild.id]
    except:
        return "="


# bot init
intents = nextcord.Intents.all()
bot = commands.Bot(command_prefix=prefix_func, help_command=None, intents=intents)


@tasks.loop(seconds=60)  # repeat after every 60 seconds
async def reconnect():
    global session
    global connected

    connected = False
    session = serversettings.connectToDatabase(uri, session)
    connected = True


@tasks.loop(minutes=1)  # repeat after every 60 seconds
async def getPrefixes():
    global session
    global prefixes

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
    reconnect.start()
    getPrefixes.start()

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
    "cogs.intreaction.functions",
    "cogs.moderation.functions",
    "cogs.milk.functions",
    "cogs.setup.functions",
    "cogs.voice.functions",
    "cogs.rp.functions",
    "cogs.arts.functions",
    "cogs.genshin.functions",
    "cogs.statcount.functions",
    "cogs.stats.functions",
    "cogs.shikimori.functions",
]

# ogs = ['cogs.milk.functions']

for cog in cogs:
    try:
        bot.load_extension(cog)
    except Exception as e:
        print(e)
        pass

bot.run(settings["token"])
