# for discord
import nextcord
from nextcord.ext import commands
from nextcord.ext.commands import Context
import datetime

import modules.database as database
from modules.checkers import check_admin_permissions
from typing import Optional

from nextcord.utils import get

from .ui import SettingsViewer


class Setup(commands.Cog, name="Установка"):
    """Настройка бота для администраторов сервера"""

    COG_EMOJI: str = "🔧"

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx: Context) -> bool:
        if ctx.guild is None:
            return True
        else:
            return check_admin_permissions(ctx)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        self.bot.database.get_guild_info(guild.id)
        self.bot.tables.create_embeds_table(guild.id)
        self.bot.tables.create_astral_table(guild.id)
        embed: nextcord.Embed = nextcord.Embed(
            title=f"{self.bot.user.name} теперь на сервере {guild.name}",
            colour=0xFF9500,
        )
        embed.add_field(
            name="=префикс", value="изменить префикс бота на сервере", inline=True
        )
        embed.add_field(
            name="=добавить_персонал",
            value="добавить персонал сервера (подробнее по справке)",
            inline=True,
        )
        embed.add_field(
            name="=удалить_персонал",
            value="удалить персонал сервера (подробнее по справке)",
            inline=True,
        )
        embed.set_footer(text=f"Спасибо за использование {self.bot.user.name}! :)")
        await guild.owner.send(embed=embed)

    @commands.command(brief="Ручная инициализация сервера")
    @commands.guild_only()
    async def инициализация(self, ctx: Context):
        self.bot.database.get_guild_info(ctx.guild.id)
        # self.bot.tables.create_art_table(ctx.guild.id)
        self.bot.tables.create_embeds_table(ctx.guild.id)
        self.bot.tables.create_astral_table(ctx.guild.id)
        await ctx.send("Inited successful!")

    @commands.command(
        brief="Активировать ежеденевную отправку аниме гороскопа",
    )
    @commands.guild_only()
    async def анимегороскоп_активация(
        self, ctx: Context, channel: Optional[nextcord.TextChannel] = None
    ):

        if isinstance(channel, nextcord.TextChannel):
            self.bot.database.set_horo(ctx.guild.id, True, channels=[channel.id])
            await ctx.send(
                f"Аниме гороскоп активирован для канала {channel.name}. "
                + "Для активации упоминания роли, используйте команду аниме_гороскоп_роль"
            )
        else:
            status: bool = self.bot.database.get_guild_info().horo
            if not status:
                return await ctx.send(
                    "Для активации аниме гороскопа, вызовите команду с упоминанием или id канала для гороскопа"
                )
            else:
                self.bot.database.set_horo(ctx.guild.id, False)
                return await ctx.send("Аниме гороскоп отключен.")

    @commands.command(
        brief="Активировать ежеденевную отправку нейро гороскопа",
    )
    @commands.guild_only()
    async def нейрогороскоп_активация(
        self, ctx: Context, channel: Optional[nextcord.TextChannel] = None
    ):

        if isinstance(channel, nextcord.TextChannel):
            self.bot.database.set_neural_horo(ctx.guild.id, True, channels=[channel.id])
            await ctx.send(
                f"Нейро гороскоп активирован для канала {channel.name}. "
                + "Для активации упоминания роли, используйте команду нейро_гороскоп_роль"
            )
        else:
            status: bool = self.bot.database.get_guild_info().neuralhoro
            if not status:
                return await ctx.send(
                    "Для активации нейро гороскопа, вызовите команду с упоминанием или id канала для гороскопа"
                )
            else:
                self.bot.database.set_neural_horo(ctx.guild.id, False)
                return await ctx.send("Гороскоп отключен.")

    @commands.command(
        brief="Активировать отправку новостей с Shikimori",
    )
    @commands.guild_only()
    async def шикиновости_активация(
        self, ctx: Context, channel: Optional[nextcord.TextChannel] = None
    ):

        if isinstance(channel, nextcord.TextChannel):
            self.bot.database.set_shikimori_news(
                ctx.guild.id, True, channels=[channel.id]
            )
            await ctx.send(f"Новости активированы для канала {channel.name}")
        else:
            status: bool = self.bot.database.get_guild_info().shikimori_news
            if not status:
                return await ctx.send(
                    "Для активации новостей с Shikimori, вызовите команду с упоминанием или id канала"
                )
            else:
                self.bot.database.set_shikimori_news(ctx.guild.id, False)
                return await ctx.send("Новости отключены.")

    @commands.command(
        brief="Активировать ежеденевную отправку релизов с Shikimori",
    )
    @commands.guild_only()
    async def шикирелизы_активация(
        self, ctx, channel: Optional[nextcord.TextChannel] = None
    ):

        if isinstance(channel, nextcord.TextChannel):
            self.bot.database.set_shikimori_releases(
                ctx.guild.id, True, channels=[channel.id]
            )
            await ctx.send(f"Релизы активированы для канала {channel.name}")
        else:
            status: bool = self.bot.database.get_guild_info().shikimori_news
            if not status:
                return await ctx.send(
                    "Для активации релизов с Shikimori, вызовите команду с упоминанием или id канала"
                )
            else:
                self.bot.database.set_shikimori_releases(ctx.guild.id, False)
                return await ctx.send("Новости отключены.")

    @commands.command(
        pass_context=True,
        brief="Активировать упоминание роли при отправке аниме гороскопа",
    )
    @commands.guild_only()
    async def анимегороскоп_роль(
        self, ctx: Context, role: Optional[nextcord.Role] = None
    ):

        if isinstance(role, nextcord.Role):
            guild_info = self.bot.database.get_guild_info(ctx.guild.id)
            self.bot.database.set_horo(
                ctx.guild.id,
                True,
                roles=[role.id],
                channels=guild_info.horo_channels,
            )
            await ctx.send(f"Активировано упоминание роли {role.name}.")
        else:
            return await ctx.send(
                "Для указания упомянаемой роли, вызовите команду с упоминанием или id роли."
            )

    @commands.command(
        pass_context=True,
        brief="Активировать упоминание роли при отправке нейро гороскопа",
    )
    @commands.guild_only()
    async def нейрогороскоп_роль(
        self, ctx: Context, role: Optional[nextcord.Role] = None
    ):

        if isinstance(role, nextcord.Role):
            guild_info = self.bot.database.get_guild_info(ctx.guild.id)
            self.bot.database.set_neural_horo(
                ctx.guild.id,
                True,
                roles=[role.id],
                channels=guild_info.neuralhoro_channels,
            )
            await ctx.send(f"Активировано упоминание роли {role.name}.")
        else:
            return await ctx.send(
                "Для указания упомянаемой роли, вызовите команду с упоминанием или id роли."
            )

    @commands.command(
        brief="Активировать упоминание роли при отправке новостей с Shikimori",
    )
    @commands.guild_only()
    async def шикиновости_роль(
        self, ctx: Context, role: Optional[nextcord.Role] = None
    ):

        if isinstance(role, nextcord.Role):
            guild_info = self.bot.database.get_guild_info(ctx.guild.id)
            self.bot.database.set_shikimori_news(
                ctx.guild.id,
                True,
                roles=[role.id],
                channels=guild_info.shikimori_news_channels,
            )
            await ctx.send(f"Активировано упоминание роли {role.name}.")
        else:
            return await ctx.send(
                "Для указания упомянаемой роли, вызовите команду с упоминанием или id роли."
            )

    @commands.command(
        brief="Активировать упоминание роли при отправке релизов с Shikimori",
    )
    @commands.guild_only()
    async def шикирелизы_роль(self, ctx: Context, role: Optional[nextcord.Role] = None):

        if isinstance(role, nextcord.Role):
            guild_info = self.bot.database.get_guild_info(ctx.guild.id)
            self.bot.database.set_shikimori_releases(
                ctx.guild.id,
                True,
                roles=[role.id],
                channels=guild_info.shikimori_releases_channels,
            )
            await ctx.send(f"Активировано упоминание роли {role.name}.")
        else:
            return await ctx.send(
                "Для указания упомянаемой роли, вызовите команду с упоминанием или id роли."
            )

    @commands.command(
        pass_context=True,
        aliases=["prefix"],
        brief="префикс",
        description="Установка нового префикса",
    )
    @commands.guild_only()
    async def префикс(self, ctx, *, префикс: Optional[str] = None):

        if префикс is None:
            return await ctx.send("Не указан префикс")

        self.bot.database.set_guild_prefix(ctx.guild.id, префикс)
        self.bot.prefixes[ctx.guild.id] = префикс
        return await ctx.send(f"Префикс изменён на {префикс}.")

    @commands.command(brief="Установка голосовых каналов")
    @commands.guild_only()
    async def инициализация_войс(
        self,
        ctx: Context,
        канал: Optional[nextcord.VoiceChannel] = None,
        категория: Optional[nextcord.CategoryChannel] = None,
    ):

        if isinstance(канал, nextcord.VoiceChannel) and isinstance(
            категория, nextcord.CategoryChannel
        ):
            self.bot.database.set_voice_channels(
                ctx.guild.id, {"category": категория.id, "generator": канал.id}
            )
            return await ctx.send(f"Успешно установлено")
        else:
            return await ctx.send("Укажите канал и категорию!")

    @commands.command(
        brief="Добавить персонал",
    )
    @commands.guild_only()
    async def добавить_персонал(self, ctx, тип: str = "", *args):

        тип = тип.lower()
        if тип not in ["админ", "модератор", "редактор"]:
            return await ctx.send("Возможные типы: админ, модератор, редактор")

        roles: list = list(args)
        if not roles:
            return await ctx.send(f"Укажите роль/роли")

        roles_id: list = []
        for role in roles:
            if role.startswith("<@&"):
                roles_id.append(int(role[3:-1]))

        match тип:
            case "админ":
                self.bot.database.add_stuff_roles(ctx.guild.id, admin_roles=roles_id)
            case "модератор":
                self.bot.database.add_stuff_roles(
                    ctx.guild.id, moderator_roles=roles_id
                )
            case "редактор":
                self.bot.database.add_stuff_roles(ctx.guild.id, editor_roles=roles_id)

        await ctx.send(f"Добавлено")

    @commands.command(
        brief="Удалить персонал",
    )
    @commands.guild_only()
    async def удалить_персонал(self, ctx, тип: str = "", *args):

        тип = тип.lower()
        if тип not in ["админ", "модератор", "редактор"]:
            return await ctx.send("Возможные типы: админ, модератор, редактор")

        roles: list = list(args)
        if not roles:
            return await ctx.send(f"Укажите роль/роли")

        roles_id: list = []
        for role in roles:
            if role.startswith("<@&"):
                roles_id.append(int(role[3:-1]))

        match тип:
            case "админ":
                self.bot.database.remove_stuff_roles(ctx.guild.id, admin_roles=roles_id)
            case "модератор":
                self.bot.database.remove_stuff_roles(
                    ctx.guild.id, moderator_roles=roles_id
                )
            case "редактор":
                self.bot.database.remove_stuff_roles(
                    ctx.guild.id, editor_roles=roles_id
                )

        await ctx.send("Удалено.")

    @commands.command(
        brief="Настройки сервера",
    )
    @commands.guild_only()
    async def настройки(self, ctx: Context):

        guild: database.GuildsSetiings = self.bot.database.get_guild_info(ctx.guild.id)

        embed = nextcord.Embed(
            title=f"Настройки бота | {ctx.guild.name}",
            description=f"Бот: **{self.bot.user.name}**\n" + f"Префикс: {guild.prefix}",
            colour=nextcord.Colour.random(),
            timestamp=datetime.datetime.now(),
        )

        if ctx.author.avatar:
            embed.set_author(
                name=ctx.author.display_name, icon_url=ctx.author.avatar.url
            )
        else:
            embed.set_author(
                name=ctx.author.display_name,
                icon_url=f"https://cdn.discordapp.com/embed/avatars/{str(int(ctx.author.discriminator) % 5)}.png",
            )

        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)

        if guild.admin_roles or guild.moderator_roles or guild.editor_roles:
            embed.add_field(
                name="Роли персонала",
                value=(
                    (
                        "Администраторы: "
                        + ", ".join(
                            [
                                ctx.guild.get_role(role_id).mention
                                for role_id in guild.admin_roles
                                if ctx.guild.get_role(role_id) is not None
                            ]
                        )
                        + "\n"
                        if guild.admin_roles
                        else ""
                    )
                    + (
                        "Модераторы:  "
                        + ", ".join(
                            [
                                ctx.guild.get_role(role_id).mention
                                for role_id in guild.moderator_roles
                                if ctx.guild.get_role(role_id) is not None
                            ]
                        )
                        + "\n"
                        if guild.moderator_roles
                        else ""
                    )
                    + (
                        f"Редакторы: "
                        ", ".join(
                            [
                                ctx.guild.get_role(role_id).mention
                                for role_id in guild.editor_roles
                                if ctx.guild.get_role(role_id) is not None
                            ]
                        )
                        + "\n"
                        if guild.editor_roles
                        else ""
                    )
                ),
                inline=False,
            )
        else:
            embed.add_field(
                name="\u200b", value="**Роли персонала не установлены**", inline=False
            )

        tables_string: str = (
            f"Embeds: https://docs.google.com/spreadsheets/d/{guild.embeds_table}/edit#gid=0"
            if guild.embeds_table
            else ""
        )
        if tables_string != "":
            embed.add_field(name="Таблицы", value=tables_string, inline=False)
        else:
            embed.add_field(
                name="\u200b", value="**Таблицы не установлены**", inline=False
            )

        if guild.voice_channel_category != 0 and guild.voice_channel_generator != 0:
            embed.add_field(
                name="Приватные текстовые каналы",
                value=(
                    (
                        "Генератор: "
                        + ctx.guild.get_channel(guild.voice_channel_generator).mention
                        if ctx.guild.get_channel(guild.voice_channel_generator)
                        is not None
                        else "Некорректный канал"
                    )
                    + "\n"
                    + (
                        "Категория: "
                        + get(
                            ctx.guild.categories, id=guild.voice_channel_category
                        ).mention
                        if get(ctx.guild.categories, id=guild.voice_channel_category)
                        is not None
                        else "Некорректная категория"
                    )
                ),
                inline=False,
            )
        else:
            embed.add_field(
                name="\u200b",
                value=f"Приватные текстовые каналы не настроены!",
                inline=False,
            )

        if guild.horo:
            embed.add_field(
                name="Аниме Гороскоп",
                value=(
                    (
                        "Роли: "
                        + ", ".join(
                            [
                                ctx.guild.get_role(role_id).mention
                                for role_id in guild.horo_roles
                                if ctx.guild.get_role(role_id) is not None
                            ]
                        )
                        + "\n"
                        if guild.horo_roles
                        else ""
                    )
                    + (
                        f"Каналы: "
                        + ", ".join(
                            [
                                ctx.guild.get_channel(channel_id).mention
                                for channel_id in guild.horo_channels
                                if ctx.guild.get_channel(channel_id) is not None
                            ]
                        )
                        + "\n"
                        if guild.horo_channels
                        else ""
                    )
                ),
                inline=False,
            )
        else:
            embed.add_field(
                name="\u200b", value="**Аниме гороскоп не активирован!**", inline=False
            )

        if guild.neuralhoro:
            embed.add_field(
                name="Нейро Гороскоп",
                value=(
                    (
                        "Роли: "
                        + ", ".join(
                            [
                                ctx.guild.get_role(role_id).mention
                                for role_id in guild.neuralhoro_roles
                                if ctx.guild.get_role(role_id) is not None
                            ]
                        )
                        + "\n"
                        if guild.neuralhoro_roles
                        else ""
                    )
                    + (
                        f"Каналы: "
                        + ", ".join(
                            [
                                ctx.guild.get_channel(channel_id).mention
                                for channel_id in guild.neuralhoro_channels
                                if ctx.guild.get_channel(channel_id) is not None
                            ]
                        )
                        + "\n"
                        if guild.neuralhoro_channels
                        else ""
                    )
                ),
                inline=False,
            )
        else:
            embed.add_field(
                name="\u200b", value="**Нейрогороскоп не активирован!**", inline=False
            )

        if guild.shikimori_news:
            embed.add_field(
                name="Новости Shikimori",
                value=(
                    (
                        "Роли: "
                        + ", ".join(
                            [
                                ctx.guild.get_role(role_id).mention
                                for role_id in guild.shikimori_news_roles
                                if ctx.guild.get_role(role_id) is not None
                            ]
                        )
                        + "\n"
                        if guild.shikimori_news_roles
                        else ""
                    )
                    + (
                        f"Каналы: "
                        + ", ".join(
                            [
                                ctx.guild.get_channel(channel_id).mention
                                for channel_id in guild.shikimori_news_channels
                                if ctx.guild.get_channel(channel_id) is not None
                            ]
                        )
                        + "\n"
                        if guild.shikimori_news_channels
                        else ""
                    )
                ),
                inline=False,
            )
        else:
            embed.add_field(
                name="\u200b",
                value="**Новости Shikimori не активированы!**",
                inline=False,
            )

        if guild.shikimori_releases:
            embed.add_field(
                name="Релизы Shikimori",
                value=(
                    (
                        "Роли: "
                        + ", ".join(
                            [
                                ctx.guild.get_role(role_id).mention
                                for role_id in guild.shikimori_releases_roles
                                if ctx.guild.get_role(role_id) is not None
                            ]
                        )
                        + "\n"
                        if guild.shikimori_releases_roles
                        else ""
                    )
                    + (
                        f"Каналы: "
                        + ", ".join(
                            [
                                ctx.guild.get_channel(channel_id).mention
                                for channel_id in guild.shikimori_releases_channels
                                if ctx.guild.get_channel(channel_id) is not None
                            ]
                        )
                        + "\n"
                        if guild.shikimori_releases_channels
                        else ""
                    )
                ),
                inline=False,
            )
        else:
            embed.add_field(
                name="\u200b",
                value="**Релизы Shikimori не активированы!**",
                inline=False,
            )

        embed_for_button: nextcord.Embed = nextcord.Embed(
            description='С целью сохранения приватности настроек бота для сервера, отправка настроек будет выполнена в скрытом режиме после нажатия на кнопку "Отправить"',
            colour=nextcord.Colour.random(),
        )

        view: SettingsViewer = SettingsViewer(ctx.author, embed)

        message: nextcord.Message = await ctx.send(embed=embed_for_button, view=view)
        await view.wait()
        await message.edit(view=None)


def setup(bot):
    bot.add_cog(Setup(bot))
