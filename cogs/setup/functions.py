# for discord
import nextcord
from nextcord.ext import commands, tasks
from nextcord.utils import get
from settings import settings

from additional.check_permission import check_admin_permissions

# database
import database.serversettings as serversettings
import database.server_init as server_init
import database.globalsettings as globalsettings
from database.updater import createTables

uri = settings["StatUri"]

# for logs
from datetime import datetime
import asyncio


class Setup(commands.Cog, name="Установка"):
    """Настройка бота для администраторов сервера"""

    COG_EMOJI = "🔧"

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, brief="Ручная инициализация сервера")
    @commands.check(check_admin_permissions)
    @commands.guild_only()
    async def инициализация(self, ctx):
        server_init.initServer(uri, ctx.guild.id)
        await ctx.send(
            "Inited successful! Для инициализации астрала, используйте комманду иницилизация-астрал"
        )

    @commands.command(
        pass_context=True,
        brief="Активировать ежеденевную отправку гороскопа",
    )
    @commands.guild_only()
    @commands.check(check_admin_permissions)
    async def гороскоп_активация(self, ctx, channel=None):

        if channel is None:
            status = serversettings.getHoroStatus(
                self.bot.databaseSession, ctx.guild.id
            )
            if not status:
                await ctx.send(
                    "Для активации гороскопа, вызовите команду с упоминанием или id канала для гороскопа"
                )
                return
            else:
                serversettings.setHoro(
                    self.bot.databaseSession, ctx.guild.id, False, None
                )
                await ctx.send("Гороскоп отключен.")
                return
        else:
            if channel.startswith("<"):
                channel = int(channel[2:-1])

        channel = self.bot.get_channel(channel)
        if channel is None:
            await ctx.send("Неверно указан канал")
            return

        serversettings.setHoro(self.bot.databaseSession, ctx.guild.id, True, channel.id)
        await ctx.send(
            f"Гороскоп активирован для канала {channel.name}. Для активации упоминания роли, используйте команду гороскоп_роль"
        )

    @commands.command(
        pass_context=True,
        brief="Активировать отправку новостей с Shikimori",
    )
    @commands.guild_only()
    @commands.check(check_admin_permissions)
    async def шикиновости_активация(self, ctx, channel=None):

        if channel is None:
            status = serversettings.getShikimoriNewsStatus(
                self.bot.databaseSession, ctx.guild.id
            )
            if not status:
                await ctx.send(
                    "Для активации новостей с Shikimori, вызовите команду с упоминанием или id канала"
                )
                return
            else:
                serversettings.setShikimoriNews(
                    self.bot.databaseSession, ctx.guild.id, False, None
                )
                await ctx.send("Новости отключены.")
                return
        else:
            if channel.startswith("<"):
                channel = int(channel[2:-1])

        channel = self.bot.get_channel(channel)
        if channel is None:
            await ctx.send("Неверно указан канал")
            return

        serversettings.setShikimoriNews(
            self.bot.databaseSession, ctx.guild.id, True, channel.id
        )
        await ctx.send(f"Новости активированы для канала {channel.name}")

    @commands.command(
        pass_context=True,
        brief="Активировать ежеденевную отправку релизов с Shikimori",
    )
    @commands.guild_only()
    @commands.check(check_admin_permissions)
    async def шикирелиз_активация(self, ctx, channel=None):

        if channel is None:
            status = serversettings.getShikimoriReleaseStatus(
                self.bot.databaseSession, ctx.guild.id
            )
            if not status:
                await ctx.send(
                    "Для активации релизов с Shikimori, вызовите команду с упоминанием или id канала"
                )
                return
            else:
                serversettings.setShikimoriRelease(
                    self.bot.databaseSession, ctx.guild.id, False, None
                )
                await ctx.send("Релизы отключены.")
                return
        else:
            if channel.startswith("<"):
                channel = int(channel[2:-1])

        channel = self.bot.get_channel(channel)
        if channel is None:
            await ctx.send("Неверно указан канал")
            return

        serversettings.setShikimoriRelease(
            self.bot.databaseSession, ctx.guild.id, True, channel.id
        )
        await ctx.send(f"Релизы активированы для канала {channel.name}")

    @commands.command(
        pass_context=True,
        brief="Активировать ежденевную отправку гороскопа",
    )
    @commands.guild_only()
    @commands.check(check_admin_permissions)
    async def гороскоп_роль(self, ctx, role=None):

        if role is None:
            await ctx.send(
                "Для активации гороскопа, вызовите команду с упоминанием или id канала для гороскопа"
            )
            return
        else:
            if role.startswith("<"):
                role = int(role[3:-1])

        role = get(ctx.guild.roles, id=role)
        if role is None:
            await ctx.send("Неверно указана роль")
            return

        serversettings.setHoroRole(self.bot.databaseSession, ctx.guild.id, role.id)
        await ctx.send(f"Активировано упоминание роли {role.name}.")

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
    @commands.check(check_admin_permissions)
    @commands.guild_only()
    async def инициализация_астрал(self, ctx):

        info = serversettings.getInfo(self.bot.databaseSession, ctx.guild.id)
        if info.astralspr is not None:
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

        serversettings.setAstralScript(self.bot.databaseSession, int(guildid), scriptid)

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
    @commands.check(check_admin_permissions)
    async def префикс(self, ctx, *, префикс):

        arg = префикс
        serversettings.setPrefix(self.bot.databaseSession, ctx.guild.id, arg)
        await ctx.send(f"Префикс будет изменён в течении минуты на {arg}.")
        return

    @commands.command(pass_context=True, brief="Установка голосовых каналов")
    @commands.guild_only()
    @commands.check(check_admin_permissions)
    async def инициализация_войс(self, ctx, *канал_категория):

        args = канал_категория
        if args != ():
            serversettings.setPrivateVoice(self.bot.databaseSession, ctx.guild.id, args)
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
            serversettings.addAdminRole(self.bot.databaseSession, ctx.guild.id, arg)
        await ctx.send(f"Админ добавлен")

    @commands.command(
        pass_context=True,
        aliases=["deladmin"],
        brief="Удалить админа",
        description="Удалить админа по id/упоминанию роли",
    )
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def удалить_админа(self, ctx, *ids):

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
            serversettings.delAdminRole(self.bot.databaseSession, ctx.guild.id, arg)
        await ctx.send(f"Админ удален")

    @commands.command(
        pass_context=True,
        aliases=["adduserrole"],
        brief="Добавить пользовательскую роль",
        description="Добавить пользовательскую роль по id/упоминанию",
    )
    @commands.guild_only()
    @commands.check(check_admin_permissions)
    async def добавить_пользователя(self, ctx, *роль):

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

        for arg in args:
            serversettings.addUserRole(self.bot.databaseSession, ctx.guild.id, arg)
        await ctx.send(f"Роли установлены")

    @commands.command(
        pass_context=True,
        brief="Настройки сервера",
        description="Отображение настроек бота для сервера",
    )
    @commands.guild_only()
    @commands.check(check_admin_permissions)
    async def настройки(self, ctx):

        info = serversettings.getInfo(session, ctx.guild.id)
        if info.prefix is not None:
            prefix = info.prefix
        else:
            prefix = "не установлено"

        emb = nextcord.Embed(
            title=f"Параметры бота для сервера {ctx.guild.name}",
            description=f"Префикс: {prefix}",
        )
        emb.color = nextcord.Colour.random()
        emb.set_thumbnail(url=ctx.guild.icon.url)

        if info.userroles is not None:
            userroles = info.userroles
        else:
            userroles = "не установлены"

        if info.adminroles is not None:
            adminroles = info.adminroles
        else:
            adminroles = "не установлено"

        emb.add_field(
            name="Роли",
            value=f"Роли для пользователей: {userroles}\nРоли для администраторов: {adminroles}",
            inline=False,
        )

        if info.embtable is not None:
            embtable = info.embtable
        else:
            embtable = "не установлено"

        if info.artspr is not None:
            artspr = info.artspr
        else:
            artspr = "не установлено"

        if info.astralspr is not None:
            astralspr = info.astralspr
        else:
            astralspr = "не установлено"

        emb.add_field(
            name="Таблицы",
            value=f"Embed: <https://docs.google.com/spreadsheets/d/{embtable}>\nAstral: <https://docs.google.com/spreadsheets/d/{astralspr}>\nArt: <https://docs.google.com/spreadsheets/d/{artspr}>",
            inline=False,
        )

        if info.voicegenerator is not None:
            voicegenerator = info.voicegenerator
        else:
            voicegenerator = "не установлено"

        if info.voicecategory is not None:
            voicecategory = info.voicecategory
        else:
            voicecategory = "не установлено"

        if info.voicemessage is not None:
            voicemessage = info.voicemessage
        else:
            voicemessage = "не установлено"

        emb.add_field(
            name="Приватные комнаты",
            value=f"Генератор: {voicegenerator}\nКатегория: {voicecategory}\nНастроечное сообщение: {voicemessage}",
            inline=False,
        )

        if info.horo:
            emb.add_field(
                name="Гороскоп",
                value=f"Состояние: {'активирован' if info.horo else 'деактивирован'}\nКанал: {info.horochannel if info.horochannel else 'неустановлен'}\nРоль: {info.hororole if info.hororole else 'неустановлена'}",
                inline=False,
            )

        else:
            emb.add_field(
                name="Гороскоп",
                value=f"Состояние: {'активирован' if info.horo else 'деактивирован'}",
                inline=False,
            )

        await ctx.send(embed=emb)
        return


def setup(bot):
    bot.add_cog(Setup(bot))
