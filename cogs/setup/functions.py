import nextcord
from nextcord.ext import commands
from nextcord.ext.commands import Context
import datetime

import modules.database as database
from modules.checkers import check_admin_permissions, app_check_admin_permissions
from typing import Optional

from nextcord.utils import get


class Setup(commands.Cog, name="Установка"):
    """Настройка бота для администраторов сервера"""

    COG_EMOJI: str = "🔧"
    COG_ID: int = 0

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx: Context) -> bool:
        if ctx.guild is None:
            return True
        else:
            return check_admin_permissions(ctx)

    @nextcord.slash_command(
        guild_ids=[], force_global=True, description="Управление рассылками"
    )
    async def mailing(self, interaction: nextcord.Interaction):
        pass

    @mailing.subcommand(
        description="Активация или деактивация определённого вида рассылки"
    )
    async def activate(
        self,
        interaction: nextcord.Interaction,
        тип: str = nextcord.SlashOption(
            description="тип рассылки",
            choices={
                "aниме гороскоп": "анимегороскоп",
                "новости шикимори": "шикиновости",
                "релизы шикимори": "шикирелизы",
            },
            required=True,
        ),
        канал: Optional[nextcord.TextChannel] = nextcord.SlashOption(
            description="канал для рассылки (оставьте пустым, если хотите отключить)",
            required=False,
        ),
    ):
        if interaction.guild is None:
            return await interaction.send("Вы не находитесь на сервере!")
        await interaction.response.defer(ephemeral=True)

        if not app_check_admin_permissions(interaction, self.bot):
            return await interaction.followup.send("Недостаточно прав!", ephemeral=True)

        match тип:
            case "анимегороскоп":
                if isinstance(канал, nextcord.TextChannel):
                    self.bot.database.set_horo(
                        interaction.guild.id, True, channels=[канал.id]
                    )
                    await interaction.followup.send(
                        f"Аниме гороскоп активирован для канала {канал.name}."
                    )
                else:
                    status: bool = self.bot.database.get_guild_info(
                        interaction.guild.id
                    ).horo
                    if not status:
                        return await interaction.followup.send(
                            "Для активации аниме гороскопа, вызовите команду с упоминанием или id канала для гороскопа"
                        )
                    else:
                        self.bot.database.set_horo(interaction.guild.id, False)
                        return await interaction.followup.send(
                            "Аниме гороскоп отключен."
                        )
            case "шикиновости":
                if isinstance(канал, nextcord.TextChannel):
                    self.bot.database.set_shikimori_news(
                        interaction.guild.id, True, channels=[канал.id]
                    )
                    await interaction.followup.send(
                        f"Новости активированы для канала {канал.name}"
                    )
                else:
                    status: bool = self.bot.database.get_guild_info(
                        interaction.guild.id
                    ).shikimori_news
                    if not status:
                        return await interaction.followup.send(
                            "Для активации новостей с Shikimori, вызовите команду с упоминанием или id канала"
                        )
                    else:
                        self.bot.database.set_shikimori_news(
                            interaction.guild.id, False
                        )
                        return await interaction.followup.send("Новости отключены.")
            case "шикирелизы":
                if isinstance(канал, nextcord.TextChannel):
                    self.bot.database.set_shikimori_releases(
                        interaction.guild.id, True, channels=[канал.id]
                    )
                    await interaction.followup.send(
                        f"Релизы активированы для канала {канал.name}"
                    )
                else:
                    status: bool = self.bot.database.get_guild_info(
                        interaction.guild.id
                    ).shikimori_news
                    if not status:
                        return await interaction.followup.send(
                            "Для активации релизов с Shikimori, вызовите команду с упоминанием или id канала"
                        )
                    else:
                        self.bot.database.set_shikimori_releases(
                            interaction.guild.id, False
                        )
                        return await interaction.followup.send("Релизы отключены.")

    @mailing.subcommand(
        description="Активация или деактивация упоминания роли при рассылке"
    )
    async def role(
        self,
        interaction: nextcord.Interaction,
        тип: str = nextcord.SlashOption(
            description="тип рассылки",
            choices={
                "aниме гороскоп": "анимегороскоп",
                "новости шикимори": "шикиновости",
                "релизы шикимори": "шикирелизы",
            },
            required=True,
        ),
        роль: Optional[nextcord.Role] = nextcord.SlashOption(
            description="упоминаемая роль (оставьте пустым, если хотите отключить)",
            required=False,
        ),
    ):
        if interaction.guild is None:
            return await interaction.send("Вы не находитесь на сервере!")
        await interaction.response.defer(ephemeral=True)

        if not app_check_admin_permissions(interaction, self.bot):
            return await interaction.followup.send("Недостаточно прав!", ephemeral=True)

        match тип:
            case "анимегороскоп":
                if isinstance(роль, nextcord.Role):
                    guild_info = self.bot.database.get_guild_info(interaction.guild.id)
                    self.bot.database.set_horo(
                        interaction.guild.id,
                        True,
                        roles=[роль.id],
                        channels=guild_info.horo_channels,
                    )
                    return await interaction.followup.send(
                        f"Активировано упоминание роли {роль.name}."
                    )
                else:
                    return await interaction.followup.send(
                        "Для указания упомянаемой роли, вызовите команду с упоминанием или id роли."
                    )
            case "шикиновости":
                if isinstance(роль, nextcord.Role):
                    guild_info = self.bot.database.get_guild_info(interaction.guild.id)
                    self.bot.database.set_shikimori_news(
                        interaction.guild.id,
                        True,
                        roles=[роль.id],
                        channels=guild_info.shikimori_news_channels,
                    )
                    return await interaction.followup.send(
                        f"Активировано упоминание роли {роль.name}."
                    )
                else:
                    return await interaction.followup.send(
                        "Для указания упомянаемой роли, вызовите команду с упоминанием или id роли."
                    )
            case "шикирелизы":
                if isinstance(роль, nextcord.Role):
                    guild_info = self.bot.database.get_guild_info(interaction.guild.id)
                    self.bot.database.set_shikimori_releases(
                        interaction.guild.id,
                        True,
                        roles=[роль.id],
                        channels=guild_info.shikimori_releases_channels,
                    )
                    return await interaction.followup.send(
                        f"Активировано упоминание роли {роль.name}."
                    )
                else:
                    return await interaction.followup.send(
                        "Для указания упомянаемой роли, вызовите команду с упоминанием или id роли."
                    )

    @nextcord.slash_command(
        guild_ids=[],
        force_global=True,
        description="Установка префикса для текстовых команд",
    )
    async def prefix(
        self,
        interaction: nextcord.Interaction,
        префикс: Optional[str] = nextcord.SlashOption(required=True),
    ):
        if interaction.guild is None:
            return await interaction.send("Вы не находитесь на сервере!")
        await interaction.response.defer()

        if not app_check_admin_permissions(interaction, self.bot):
            return await interaction.followup.send("Недостаточно прав!", ephemeral=True)

        self.bot.database.set_guild_prefix(interaction.guild.id, префикс)
        self.bot.prefixes[interaction.guild.id] = префикс
        return await interaction.followup.send(f"Префикс изменён на {префикс}.")

    @nextcord.slash_command(
        guild_ids=[],
        force_global=True,
        description="Инициализация временных голосовых каналов",
    )
    async def init_temp_voice_channels(
        self,
        interaction: nextcord.Interaction,
        канал: Optional[nextcord.VoiceChannel] = nextcord.SlashOption(required=True),
    ):
        if interaction.guild is None:
            return await interaction.send("Вы не находитесь на сервере!")
        await interaction.response.defer()

        if not app_check_admin_permissions(interaction, self.bot):
            return await interaction.followup.send("Недостаточно прав!", ephemeral=True)

        if канал.category is None:
            return await interaction.followup.send("Канал не находится в категории!")

        if isinstance(канал, nextcord.VoiceChannel):
            self.bot.database.set_voice_channels(
                interaction.guild.id,
                {"category": канал.category.id, "generator": канал.id},
            )
            return await interaction.followup.send("Успешно установлено")
        else:
            return await interaction.followup.send("Укажите канал и категорию!")

    @nextcord.slash_command(
        guild_ids=[], force_global=True, description="Управление персоналом"
    )
    async def stuff(self, interaction: nextcord.Interaction):
        pass

    @stuff.subcommand(description="Добавить персонал")
    async def add(
        self,
        interaction: nextcord.Interaction,
        тип: str = nextcord.SlashOption(
            description="тип персонала",
            choices={
                "aдмин": "админ",
                "модератор": "модератор",
                "редактор": "редактор",
            },
            required=True,
        ),
        роли: str = nextcord.SlashOption(
            description="упоминания ролей, перечисленные через запятую", required=True
        ),
    ):
        if interaction.guild is None:
            return await interaction.send("Вы не находитесь на сервере!")
        await interaction.response.defer(ephemeral=True)

        if not app_check_admin_permissions(interaction, self.bot):
            return await interaction.followup.send("Недостаточно прав!", ephemeral=True)

        roles = роли.replace(" ", "").replace("<@&", "").replace(">", "").split(",")
        roles_id = list(map(int, roles))

        match тип:
            case "админ":
                self.bot.database.add_stuff_roles(
                    interaction.guild.id, admin_roles=roles_id
                )
            case "модератор":
                self.bot.database.add_stuff_roles(
                    interaction.guild.id, moderator_roles=roles_id
                )
            case "редактор":
                self.bot.database.add_stuff_roles(
                    interaction.guild.id, editor_roles=roles_id
                )

        await interaction.followup.send("Успешно добавлены", ephemeral=True)

    @stuff.subcommand(description="Удалить персонал")
    async def remove(
        self,
        interaction: nextcord.Interaction,
        тип: str = nextcord.SlashOption(
            description="тип персонала",
            choices={
                "aдмин": "админ",
                "модератор": "модератор",
                "редактор": "редактор",
            },
            required=True,
        ),
        роли: str = nextcord.SlashOption(
            description="упоминания ролей, перечисленные через запятую", required=True
        ),
    ):
        if interaction.guild is None:
            return await interaction.send("Вы не находитесь на сервере!")
        await interaction.response.defer(ephemeral=True)

        if not app_check_admin_permissions(interaction, self.bot):
            return await interaction.followup.send("Недостаточно прав!", ephemeral=True)

        roles = роли.replace(" ", "").replace("<@&", "").replace(">", "").split(",")
        roles_id = list(map(int, roles))

        match тип:
            case "админ":
                self.bot.database.remove_stuff_roles(
                    interaction.guild.id, admin_roles=roles_id
                )
            case "модератор":
                self.bot.database.remove_stuff_roles(
                    interaction.guild.id, moderator_roles=roles_id
                )
            case "редактор":
                self.bot.database.remove_stuff_roles(
                    interaction.guild.id, editor_roles=roles_id
                )

        await interaction.followup.send("Успешно удалены", ephemeral=True)

    @nextcord.slash_command(
        guild_ids=[], force_global=True, description="Текущие настройки сервера"
    )
    async def current_settings(self, interaction: nextcord.Interaction):
        if interaction.guild is None:
            return await interaction.send("Вы не находитесь на сервере!")
        await interaction.response.defer(ephemeral=True)

        if not app_check_admin_permissions(interaction, self.bot):
            return await interaction.followup.send("Недостаточно прав!", ephemeral=True)

        guild: database.GuildsSetiings = self.bot.database.get_guild_info(
            interaction.guild.id
        )

        embed = nextcord.Embed(
            title=f"Настройки бота | {interaction.guild.name}",
            description=f"Бот: **{self.bot.user.name}**\n" + f"Префикс: {guild.prefix}",
            colour=nextcord.Colour.random(),
            timestamp=datetime.datetime.now(),
        )

        if interaction.user.avatar:
            embed.set_author(
                name=interaction.user.display_name, icon_url=interaction.user.avatar.url
            )
        else:
            embed.set_author(
                name=interaction.user.display_name,
                icon_url=f"https://cdn.discordapp.com/embed/avatars/{str(int(interaction.user.discriminator) % 5)}.png",
            )

        if interaction.guild.icon:
            embed.set_thumbnail(url=interaction.guild.icon.url)

        if guild.admin_roles or guild.moderator_roles or guild.editor_roles:
            embed.add_field(
                name="Роли персонала",
                value=(
                    (
                        "Администраторы: "
                        + ", ".join(
                            [
                                interaction.guild.get_role(role_id).mention
                                for role_id in guild.admin_roles
                                if interaction.guild.get_role(role_id) is not None
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
                                interaction.guild.get_role(role_id).mention
                                for role_id in guild.moderator_roles
                                if interaction.guild.get_role(role_id) is not None
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
                                interaction.guild.get_role(role_id).mention
                                for role_id in guild.editor_roles
                                if interaction.guild.get_role(role_id) is not None
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

        if guild.voice_channel_category != 0 and guild.voice_channel_generator != 0:
            embed.add_field(
                name="Приватные текстовые каналы",
                value=(
                    (
                        "Генератор: "
                        + interaction.guild.get_channel(
                            guild.voice_channel_generator
                        ).mention
                        if interaction.guild.get_channel(guild.voice_channel_generator)
                        is not None
                        else "Некорректный канал"
                    )
                    + "\n"
                    + (
                        "Категория: "
                        + get(
                            interaction.guild.categories,
                            id=guild.voice_channel_category,
                        ).mention
                        if get(
                            interaction.guild.categories,
                            id=guild.voice_channel_category,
                        )
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
                                interaction.guild.get_role(role_id).mention
                                for role_id in guild.horo_roles
                                if interaction.guild.get_role(role_id) is not None
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
                                interaction.guild.get_channel(channel_id).mention
                                for channel_id in guild.horo_channels
                                if interaction.guild.get_channel(channel_id) is not None
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

        if guild.shikimori_news:
            embed.add_field(
                name="Новости Shikimori",
                value=(
                    (
                        "Роли: "
                        + ", ".join(
                            [
                                interaction.guild.get_role(role_id).mention
                                for role_id in guild.shikimori_news_roles
                                if interaction.guild.get_role(role_id) is not None
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
                                interaction.guild.get_channel(channel_id).mention
                                for channel_id in guild.shikimori_news_channels
                                if interaction.guild.get_channel(channel_id) is not None
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
                                interaction.guild.get_role(role_id).mention
                                for role_id in guild.shikimori_releases_roles
                                if interaction.guild.get_role(role_id) is not None
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
                                interaction.guild.get_channel(channel_id).mention
                                for channel_id in guild.shikimori_releases_channels
                                if interaction.guild.get_channel(channel_id) is not None
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

        await interaction.followup.send(embed=embed, ephemeral=True)


def setup(bot):
    bot.add_cog(Setup(bot))
