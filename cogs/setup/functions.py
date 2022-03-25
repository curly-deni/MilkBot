# This is executable for the first server of MilkBot

# for discord
import nextcord
from nextcord.ext import commands
from nextcord.ext import tasks
from nextcord.utils import get
from settings import settings

# database
session = None
connected = False
import database.serversettings as serversettings
import database.server_init as server_init
import database.globalsettings as globalsettings
from database.updater import createTables

uri = settings["StatUri"]

# for logs
from datetime import datetime
import asyncio

from additional.check_permission import check_permission


@tasks.loop(seconds=120)  # repeat after every 60 seconds
async def reconnect():
    global session
    global connected

    connected = False
    session = serversettings.connectToDatabase(uri, session)
    connected = True


class Setup(commands.Cog, name="Установка"):
    """Настройка бота для администраторов сервера"""

    COG_EMOJI = "🔧"

    def __init__(self, bot):
        self.bot = bot
        reconnect.start()

    @commands.command(pass_context=True, brief="Ручная инициализация сервера")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def инициализация(self, ctx):
        server_init.initServer(uri, ctx.guild.id)
        await ctx.send(
            "Inited successful! Для инициализации астрала, используйте комманду иницилизация-астрал"
        )

    @commands.command(pass_context=True, brief="Обновление баз данных")
    @commands.is_owner()
    async def бд_обновление(self, ctx, таблица=None):

        if таблица is None:
            await ctx.send("Укажите имя таблицы")
            return

        guilds = []
        for guild in self.bot.guilds:
            guilds.append(guild.id)

        try:
            createTables(uri, guilds, таблица)
            await ctx.send("Успешное обновление")
        except Exception as e:
            await ctx.send(f"При обновлении произошла ошибка: {e}")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        server_init.initServer(uri, guild.id)
        embed = nextcord.Embed(
            title=f"{self.bot.user.name} теперь на сервере {guild.name}", color=0xFF9500
        )
        embed.add_field(
            name="=префикс", value="изменить префикс бота на сервере", inline=True
        )
        embed.add_field(
            name="=добавить_админа",
            value="добавить роль администратора по id",
            inline=True,
        )
        embed.add_field(
            name="=удалить_админа",
            value="удалить роль администратора по id",
            inline=True,
        )
        embed.set_footer(text=f"Спасибо за использование {self.bot.user.name}! :)")
        await guild.owner.send(embed=embed)

    @commands.command(
        pass_context=True,
        brief="иницализация астрала",
        description="Отправка запроса на активацию Астрала",
    )
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def инициализация_астрал(self, ctx):
        global session

        info = serversettings.getInfo(session, ctx.guild.id)
        if info.astralspr != None:
            astralspr = info.astraltable
        else:
            astralspr = "не установлено"

        emb = nextcord.Embed(title="Запрос на активацию астрала.")

        emb.add_field(name=f"{ctx.guild.name}", value=f"{ctx.guild.id}")

        emb.add_field(
            name="Таблица",
            value=f"<https://docs.google.com/spreadsheets/d/{astralspr}>",
            inline=False,
        )

        emb.set_footer(
            text="Запрос на активацию будет удовлетворён в течении трёх дней."
        )

        channel = await self.bot.fetch_channel(940850304444932158)
        await ctx.send(embed=emb)
        await channel.send(embed=emb)

    @commands.command(
        pass_context=True,
        brief="Установка астрал-скрипт",
        description="Установка астрал-скрипт",
    )
    @commands.is_owner()
    @commands.guild_only()
    async def астрал_скрипт(self, ctx, guildid=None, scriptid=None):
        global session

        serversettings.setAstralScript(session, int(guildid), scriptid)

        guild = get(self.bot.guilds, id=int(guildid))
        await ctx.send("Астрал активирован")
        await guild.owner.send("Астрал активирован")

    @commands.command(
        pass_context=True,
        aliases=["prefix"],
        brief="префикс",
        description="Установка нового префикс",
    )
    @commands.guild_only()
    async def префикс(self, ctx, *, префикс):
        global session

        arg = префикс
        adminroles = serversettings.getAdminRole(session, ctx.guild.id)
        if check_permission(ctx.author.roles, adminroles):
            serversettings.setPrefix(session, ctx.guild.id, arg)
            await ctx.send(f"Префикс будет изменён в течении минуты на {arg}.")
            return

    @commands.command(pass_context=True, brief="Установка голосовых каналов")
    @commands.guild_only()
    async def инициализация_войс(self, ctx, *канал_категория):
        global session

        args = канал_категория
        if args != ():
            adminroles = serversettings.getAdminRole(session, ctx.guild.id)
            if check_permission(ctx.author.roles, adminroles):
                serversettings.setPrivateVoice(session, ctx.guild.id, args)
                await ctx.send(f"Успешно установлено")
        else:
            await ctx.send(f"Не указан канал и категория.")

    @commands.command(
        pass_context=True,
        aliases=["addadmin"],
        brief="Добавить админа",
        description="Добавить админа по id/упоминанию роли",
    )
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def добавить_админа(self, ctx, *ids):
        global session

        args = ids
        g = []
        if args == ():
            await ctx.send(f"Укажите роль")
            return
        for arg in args:
            if arg.startswith("<@&"):
                g.append(arg[3:-1])
        if g != []:
            args = g

        for arg in args:
            serversettings.addAdminRole(session, ctx.guild.id, arg)
        await ctx.send(f"Админ добавлен")

    @commands.command(
        pass_context=True,
        aliases=["deladmin"],
        brief="Удалить админа",
        description="Добавить админа по id/упоминанию роли",
    )
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def удалить_админа(self, ctx, *ids):
        global session

        args = ids
        g = []
        if args == ():
            await ctx.send(f"Укажите роль")
            return
        for arg in args:
            if arg.startswith("<@&"):
                g.append(arg[3:-1])
        if g != []:
            args = g

        for arg in args:
            serversettings.delAdminRole(session, ctx.guild.id, arg)
        await ctx.send(f"Админ удален")

    @commands.command(
        pass_context=True,
        aliases=["adduserrole"],
        brief="Добавить пользовательскую роль",
        description="Добавить пользовательскую роль по id/упоминанию",
    )
    @commands.guild_only()
    async def добавить_пользователя(self, ctx, *роль):
        global session
        args = роль
        g = []
        if args == ():
            await ctx.send(f"Укажите роль")
            return
        for arg in args:
            if arg.startswith("<@&"):
                g.append(arg[3:-1])
            else:
                g.append(arg)
        if g != []:
            args = g

        adminroles = serversettings.getAdminRole(session, ctx.guild.id)
        if check_permission(ctx.author.roles, adminroles):
            for arg in args:
                serversettings.addUserRole(session, ctx.guild.id, arg)
            await ctx.send(f"Роли установлены")

    @commands.command(
        pass_context=True,
        brief="Настройки сервера",
        description="Отображение настроек бота для сервера",
    )
    @commands.guild_only()
    async def настройки(self, ctx):
        global session
        global session

        adminroles = serversettings.getAdminRole(session, ctx.guild.id)
        if check_permission(ctx.author.roles, adminroles):
            info = serversettings.getInfo(session, ctx.guild.id)
            if info.prefix != None:
                prefix = info.prefix
            else:
                prefix = "не установлено"

            emb = nextcord.Embed(
                title=f"Параметры бота для сервера {ctx.guild.name}",
                description=f"Префикс: {prefix}",
            )
            emb.color = nextcord.Colour.random()
            emb.set_thumbnail(url=ctx.guild.icon.url)

            if info.userroles != None:
                userroles = info.userroles
            else:
                userroles = "не установлены"

            if info.adminroles != None:
                adminroles = info.adminroles
            else:
                adminroles = "не установлено"

            emb.add_field(
                name="Роли",
                value=f"Роли для пользователей: {userroles}\nРоли для администраторов: {adminroles}",
                inline=False,
            )

            if info.embtable != None:
                embtable = info.embtable
            else:
                embtable = "не установлено"

            if info.artspr != None:
                artspr = info.artspr
            else:
                artspr = "не установлено"

            if info.astralspr != None:
                astralspr = info.astralspr
            else:
                astralspr = "не установлено"

            emb.add_field(
                name="Таблицы",
                value=f"Embed: <https://docs.google.com/spreadsheets/d/{embtable}>\nAstral: <https://docs.google.com/spreadsheets/d/{astralspr}>\nArt: <https://docs.google.com/spreadsheets/d/{artspr}>",
                inline=False,
            )

            if info.voicegenerator != None:
                voicegenerator = info.voicegenerator
            else:
                voicegenerator = "не установлено"

            if info.voicecategory != None:
                voicecategory = info.voicecategory
            else:
                voicecategory = "не установлено"

            emb.add_field(
                name="Приватные комнаты",
                value=f"Генератор: {voicegenerator}\nКатегория: {voicecategory}",
                inline=False,
            )
            await ctx.send(embed=emb)
            return
        else:
            await ctx.send("Добавьте роли администраторов!")


def setup(bot):
    bot.add_cog(Setup(bot))
