from datetime import datetime
from typing import Optional

import modules.database as database
import nextcord
from base.base_cog import MilkCog
from nextcord.utils import get

from .ui import GIFandImageSetuper, ReactionRolesSetup, VerifyReactionRolesSetup


class Setup(MilkCog, name="Установка"):
    """Настройка бота для администраторов сервера"""

    COG_EMOJI: str = "🔧"

    def __init__(self, bot):
        self.bot = bot
        self.required_permission = "admin"

    @MilkCog.slash_command()
    async def config(self, interaction):
        ...

    @config.subcommand()
    async def mailing(self, interaction: nextcord.Interaction):
        pass

    @mailing.subcommand(
        description="Активация или деактивация определённого вида рассылки"
    )
    async def activate(
        self,
        interaction: nextcord.Interaction,
        type: str = nextcord.SlashOption(
            name="тип",
            description="тип рассылки",
            choices={
                "aниме гороскоп": "анимегороскоп",
                "новости шикимори": "шикиновости",
                "релизы шикимори": "шикирелизы",
            },
            required=True,
        ),
        channel: Optional[nextcord.TextChannel] = nextcord.SlashOption(
            name="канал",
            description="канал для рассылки (оставьте пустым, если хотите отключить)",
            required=False,
        ),
    ):
        await interaction.response.defer()
        match type:
            case "анимегороскоп":
                if isinstance(channel, nextcord.TextChannel):
                    self.bot.database.set_horo(
                        interaction.guild.id, True, channels=[channel.id]
                    )
                    await interaction.followup.send(
                        f"Аниме гороскоп активирован для channelа {channel.name}."
                    )
                else:
                    status: bool = self.bot.database.get_guild_info(
                        interaction.guild.id
                    ).horo
                    if not status:
                        return await interaction.followup.send(
                            "Для активации аниме гороскопа, вызовите команду с упоминанием или id channelа для гороскопа"
                        )
                    else:
                        self.bot.database.set_horo(interaction.guild.id, False)
                        return await interaction.followup.send(
                            "Аниме гороскоп отключен."
                        )
            case "шикиновости":
                if isinstance(channel, nextcord.TextChannel):
                    self.bot.database.set_shikimori_news(
                        interaction.guild.id, True, channels=[channel.id]
                    )
                    await interaction.followup.send(
                        f"Новости активированы для channelа {channel.name}"
                    )
                else:
                    status: bool = self.bot.database.get_guild_info(
                        interaction.guild.id
                    ).shikimori_news
                    if not status:
                        return await interaction.followup.send(
                            "Для активации новостей с Shikimori, вызовите команду с упоминанием или id channelа"
                        )
                    else:
                        self.bot.database.set_shikimori_news(
                            interaction.guild.id, False
                        )
                        return await interaction.followup.send("Новости отключены.")
            case "шикирелизы":
                if isinstance(channel, nextcord.TextChannel):
                    self.bot.database.set_shikimori_releases(
                        interaction.guild.id, True, channels=[channel.id]
                    )
                    await interaction.followup.send(
                        f"Релизы активированы для channelа {channel.name}"
                    )
                else:
                    status: bool = self.bot.database.get_guild_info(
                        interaction.guild.id
                    ).shikimori_news
                    if not status:
                        return await interaction.followup.send(
                            "Для активации релизов с Shikimori, вызовите команду с упоминанием или id channelа"
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
        type: str = nextcord.SlashOption(
            name="type",
            description="тип рассылки",
            choices={
                "aниме гороскоп": "анимегороскоп",
                "новости шикимори": "шикиновости",
                "релизы шикимори": "шикирелизы",
            },
            required=True,
        ),
        role: Optional[nextcord.Role] = nextcord.SlashOption(
            name="роль",
            description="упоминаемая роль (оставьте пустым, если хотите отключить)",
            required=False,
        ),
    ):
        await interaction.response.defer()
        match type:
            case "анимегороскоп":
                if isinstance(role, nextcord.Role):
                    guild_info = self.bot.database.get_guild_info(interaction.guild.id)
                    self.bot.database.set_horo(
                        interaction.guild.id,
                        True,
                        roles=[role.id],
                        channels=guild_info.horo_channels,
                    )
                    return await interaction.followup.send(
                        f"Активировано упоминание роли {role.name}."
                    )
                else:
                    return await interaction.followup.send(
                        "Для указания упомянаемой роли, вызовите команду с упоминанием или id роли."
                    )
            case "шикиновости":
                if isinstance(role, nextcord.Role):
                    guild_info = self.bot.database.get_guild_info(interaction.guild.id)
                    self.bot.database.set_shikimori_news(
                        interaction.guild.id,
                        True,
                        roles=[role.id],
                        channels=guild_info.shikimori_news_channels,
                    )
                    return await interaction.followup.send(
                        f"Активировано упоминание роли {role.name}."
                    )
                else:
                    return await interaction.followup.send(
                        "Для указания упомянаемой роли, вызовите команду с упоминанием или id роли."
                    )
            case "шикирелизы":
                if isinstance(role, nextcord.Role):
                    guild_info = self.bot.database.get_guild_info(interaction.guild.id)
                    self.bot.database.set_shikimori_releases(
                        interaction.guild.id,
                        True,
                        roles=[role.id],
                        channels=guild_info.shikimori_releases_channels,
                    )
                    return await interaction.followup.send(
                        f"Активировано упоминание роли {role.name}."
                    )
                else:
                    return await interaction.followup.send(
                        "Для указания упомянаемой роли, вызовите команду с упоминанием или id роли."
                    )

    @config.subcommand(description="Установка префикса для текстовых команд")
    async def prefix(
        self,
        interaction: nextcord.Interaction,
        prefix: Optional[str] = nextcord.SlashOption(
            name="префикс",
            description="префикс текстовых каналов",
            min_length=1,
            required=True,
        ),
    ):

        await interaction.response.defer()

        self.bot.database.set_guild_prefix(interaction.guild.id, prefix)
        self.bot.prefixes[interaction.guild.id] = prefix
        return await interaction.followup.send(f"Префикс изменён на {prefix}.")

    @config.subcommand(
        description="Инициализация временных голосовых каналов",
    )
    async def voice_channels(
        self,
        interaction: nextcord.Interaction,
        channel: Optional[nextcord.VoiceChannel] = nextcord.SlashOption(
            name="канал",
            description='Голосовой канал-"генератор", находящийся в категории',
            required=True,
        ),
    ):

        await interaction.response.defer()

        if channel.category is None:
            return await interaction.followup.send("Канал не находится в категории!")

        if isinstance(channel, nextcord.VoiceChannel):
            self.bot.database.set_voice_channels(
                interaction.guild.id,
                {"category": channel.category.id, "generator": channel.id},
            )
            return await interaction.followup.send("Успешно установлено")
        else:
            return await interaction.followup.send("Укажите канал и категорию!")

    @config.subcommand()
    async def stuff(self, interaction: nextcord.Interaction):
        pass

    @stuff.subcommand(description="Добавить персонал")
    async def add(
        self,
        interaction: nextcord.Interaction,
        type: str = nextcord.SlashOption(
            name="тип",
            description="тип персонала",
            choices={
                "aдмин": "админ",
                "модератор": "модератор",
                "редактор": "редактор",
            },
            required=True,
        ),
        roles: str = nextcord.SlashOption(
            name="роли",
            description="упоминания ролей, перечисленные через запятую",
            required=True,
        ),
    ):

        await interaction.response.defer(ephemeral=True)

        roles = roles.replace(" ", "").replace("<@&", "").replace(">", "").split(",")
        roles_id = list(map(int, roles))

        match type:
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
        type: str = nextcord.SlashOption(
            name="тип",
            description="тип персонала",
            choices={
                "aдмин": "админ",
                "модератор": "модератор",
                "редактор": "редактор",
            },
            required=True,
        ),
        roles: str = nextcord.SlashOption(
            name="роли",
            description="упоминания ролей, перечисленные через запятую",
            required=True,
        ),
    ):

        await interaction.response.defer(ephemeral=True)

        roles = roles.replace(" ", "").replace("<@&", "").replace(">", "").split(",")
        roles_id = list(map(int, roles))

        match type:
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

    @config.subcommand(description="Текущие настройки сервера")
    async def current(self, interaction: nextcord.Interaction):

        await interaction.response.defer(ephemeral=True)

        guild: database.GuildsSetiings = self.bot.database.get_guild_info(
            interaction.guild.id
        )

        embed = nextcord.Embed(
            title=f"Настройки бота | {interaction.guild.name}",
            description=f"Бот: **{self.bot.user.name}**\n" + f"Префикс: {guild.prefix}",
            colour=nextcord.Colour.random(),
            timestamp=datetime.now(),
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

    @config.subcommand()
    async def restore_roles(
        self,
        interaction: nextcord.Interaction,
    ):
        ...

    @restore_roles.subcommand(
        name="disable",
        description="Выключение возврата ролей для вернувшихся пользователей",
    )
    async def restore_roles_disable(
        self,
        interaction: nextcord.Interaction,
    ):
        await interaction.response.defer(ephemeral=True)
        db_info = self.bot.database.get_guild_info(interaction.guild.id)
        db_info.restore_roles = False
        await interaction.followup.send("Возврат ролей отключен!")
        self.bot.database.session.commit()

    @restore_roles.subcommand(
        name="enable",
        description="Включение возврата ролей для вернувшихся пользователей",
    )
    async def restore_roles_enable(
        self,
        interaction: nextcord.Interaction,
        need_verify: bool = nextcord.SlashOption(
            name="необходима_верефикация",
            description="Необходма ли верефикация через MilkBot, для возвращения ролей",
        ),
    ):
        await interaction.response.defer(ephemeral=True)
        db_info = self.bot.database.get_guild_info(interaction.guild.id)
        db_info.restore_roles = True
        if need_verify and not db_info.verify:
            await interaction.followup.send(
                "Возврат ролей после верефикации включен. "
                + "**ВНИМАНИЕ:** Верификация не настроена через MilkBot"
            )
        elif need_verify:
            await interaction.followup.send("Возврат ролей после верефикации включен.")
        else:
            await interaction.followup.send("Возврат ролей включен.")
        self.bot.database.session.commit()

    @config.subcommand()
    async def reaction_roles(self, interaction: nextcord.Interaction):
        ...

    @reaction_roles.subcommand(
        name="create", description="Создание сообщения для выдачи роли по реакциям"
    )
    async def reaction_roles_create(
        self,
        interaction: nextcord.Interaction,
        channel: nextcord.TextChannel = nextcord.SlashOption(
            name="канал",
            description="Текстовый канал, в котором небоходимо создать Reaction Roles",
            required=True,
        ),
        new_embed: bool = nextcord.SlashOption(
            name="новое_сообщение",
            description="Необходимо ли отправлять новое сообщение",
            choices={
                "Да": True,
                "Нет": False,
            },
            required=True,
        ),
        id: str = nextcord.SlashOption(
            name="id",
            description="ID существующего сообщения, в которое нужно добавить Reaction Roles",
            required=False,
        ),
    ):
        if not new_embed:
            await interaction.response.defer(ephemeral=True)
            try:
                message = await channel.fetch_message(int(id))
            except:
                await interaction.followup.send(f"Не найдено сообщения с ID {id}")
                return
            if message is None:
                await interaction.followup.send(f"Не найдено сообщения с ID {id}")
                return
        else:
            message = None

        view = ReactionRolesSetup(interaction.user, self.bot, channel, message)
        control_message = await interaction.send(view=view)
        content_message = (
            f"**Только одна выбранная роль:** {'Да' if view.unique else 'Нет'}\n"
            + f"**Однократное использование:** {'Да' if view.single_use else 'Нет'}"
            + ("\n\n" + view.message_text if view.message_text != "" else "")
        )
        preview_message = await interaction.followup.send(
            content=content_message, embed=view.embed
        )
        view.control_message = control_message
        view.preview_message = preview_message
        view.original_channel = interaction.channel
        await view.wait()

    @reaction_roles.subcommand(
        name="edit",
        description="Редактирование сообщения для выдачи роли по реакциям",
    )
    async def reaction_roles_edit(
        self,
        interaction: nextcord.Interaction,
        channel: nextcord.TextChannel = nextcord.SlashOption(
            name="канал",
            description="Текстовый канал, в котором находится сообщение",
            required=True,
        ),
        edit_existing: bool = nextcord.SlashOption(
            name="редактировать_сообщение",
            description="Необходимо ли отредактировать сообщение (бот должен быть автором сообщения)",
            choices={
                "Да": True,
                "Нет": False,
            },
            required=True,
        ),
        id: str = nextcord.SlashOption(
            name="id",
            description="ID-сообщения, в котором находится Reaction Roles",
            required=True,
        ),
    ):
        await interaction.response.defer(ephemeral=True)
        try:
            message = await channel.fetch_message(int(id))
        except:
            await interaction.followup.send(f"Не найдено сообщения с ID {id}")
            return
        if message is None:
            await interaction.followup.send(f"Не найдено сообщения с ID {id}")
            return

        db_info = self.bot.database.get_reaction_roles_info(message.id, channel.id)
        if db_info is None:
            await interaction.followup.send(
                "В БД не обнаружено записей об этом сообщении"
            )
            return

        if interaction.user.id != db_info.author_id:
            await interaction.followup.send(f"Вы не являетесь автором этого блока")
            return

        if edit_existing and message.author != self.bot.user:
            await interaction.followup.send(f"Бот не является автором этого соообщения")
            return

        view = ReactionRolesSetup(
            interaction.user, self.bot, channel, message, db_info, edit_existing
        )
        control_message = await interaction.followup.send(view=view)
        content_message = (
            f"**Только одна выбранная роль:** {'Да' if view.unique else 'Нет'}\n"
            + f"**Однократное использование:** {'Да' if view.single_use else 'Нет'}"
            + ("\n\n" + view.message_text if view.message_text != "" else "")
        )
        preview_message = await interaction.followup.send(
            content=content_message, embed=view.embed
        )
        for emoji in view.reaction_and_roles:
            await preview_message.add_reaction(emoji)
        view.control_message = control_message
        view.preview_message = preview_message
        view.original_channel = interaction.channel
        await view.wait()

    @reaction_roles.subcommand(
        name="delete", description="Удаление сообщения для выдачи роли по реакциям"
    )
    async def reaction_roles_delete(
        self,
        interaction: nextcord.Interaction,
        channel: nextcord.TextChannel = nextcord.SlashOption(
            name="канал",
            description="Текстовый канал, в котором находится сообщение",
            required=True,
        ),
        id: str = nextcord.SlashOption(
            name="id",
            description="ID-сообщения, в котором находится Reaction Roles",
            required=True,
        ),
    ):
        await interaction.response.defer(ephemeral=True)
        try:
            message = await channel.fetch_message(int(id))
        except:
            await interaction.followup.send(f"Не найдено сообщения с ID {id}")
            return
        if message is None:
            await interaction.followup.send(f"Не найдено сообщения с ID {id}")
            return

        db_info = self.bot.database.get_reaction_roles_info(message.id, channel.id)
        if db_info is None:
            await interaction.followup.send(
                "В БД не обнаружено записей об этом сообщении"
            )
            return

        if interaction.user.id != db_info.author_id:
            await interaction.followup.send(f"Вы не являетесь автором этого блока")
            return
        if not db_info.sended_message:
            await message.clear_reactions()
        else:
            await message.delete()
        self.bot.database.delete_reaction_roles_info(message.id, channel.id)
        await interaction.followup.send("ReactionRoles успешно удалён")

    @MilkCog.slash_command(
        description="Редактирование изображений и гифок для RP сообщений",
        permission="moderator",
    )
    async def rp_gif_setup(
        self,
        interaction: nextcord.Interaction,
        type: str = nextcord.SlashOption(
            name="действие",
            description="название действия",
            choices={
                "обьятие": "hug",
                "улыбка": "smile",
                "тык": "poke",
                "пощёчина": "slap",
                "укус": "bite",
                "рыдание": "cry",
                "краснение": "blush",
                "поцелуй": "kiss",
                "облизывание": "lick",
                "поглаживание": "pat",
                "кормление": "feed",
            },
            required=True,
        ),
    ):
        info = self.bot.database.get_guild_rp_custom_gif(interaction.guild.id)
        gif = []
        exec(f"gif.extend(info.{type})")

        view = GIFandImageSetuper(interaction.user, self.bot, gif, type)
        control_message = await interaction.send(view=view)
        preview_message = await interaction.followup.send(embed=view.embed)
        view.control_message = control_message
        view.preview_message = preview_message
        await view.wait()

        info = self.bot.database.get_guild_rp_custom_gif(interaction.guild.id)
        exec(f"info.{type} = view.gif_list")
        self.bot.database.session.commit()
        await interaction.followup.send("Успешно обновлено!")

    @config.subcommand()
    async def verify(self, interaction):
        ...

    @verify.subcommand(
        name="classic_setup", description="Настройка верификации через MilkBot"
    )
    async def verify_setup(
        self,
        interaction: nextcord.Interaction,
        activate: bool = nextcord.SlashOption(
            name="включена", description="Состояние верификации"
        ),
        roles: str = nextcord.SlashOption(
            name="роли",
            description="Написанные через запятую упоминания ролей для верификации",
            required=False,
        ),
    ):
        await interaction.response.defer(ephemeral=True)
        guild_info = self.bot.database.get_guild_info(interaction.guild.id)
        if activate:
            roles = (
                roles.replace(" ", "").replace("<@&", "").replace(">", "").split(",")
            )
            roles_id = list(map(int, roles))

            valid_roles = [
                interaction.guild.get_role(role_id)
                for role_id in roles_id
                if interaction.guild.get_role(role_id) is not None
            ]

            guild_info.verify = True
            guild_info.verify_roles = [role.id for role in valid_roles]

            await interaction.followup.send(
                "Верификация активирована! Роли для верификации: "
                + ", ".join([role.mention for role in valid_roles])
            )
        else:
            guild_info.verify = False
            await interaction.followup.send("Верификация деактивирована")
        await self.bot.database.session.commit()

    @verify.subcommand(
        name="reaction_roles_setup",
        description="Создание ReactionRoles сообщения для верификации",
    )
    async def verify_reaction_roles_create(
        self,
        interaction: nextcord.Interaction,
        channel: nextcord.TextChannel = nextcord.SlashOption(
            name="канал",
            description="Текстовый канал, в котором небоходимо создать Reaction Roles",
            required=True,
        ),
    ):
        view = VerifyReactionRolesSetup(interaction.user, self.bot, channel)
        control_message = await interaction.send(view=view)
        preview_message = await interaction.followup.send(
            content=view.message_text, embed=view.embed
        )
        view.control_message = control_message
        view.preview_message = preview_message
        view.original_channel = interaction.channel
        await view.wait()

    @verify.subcommand(name="notify", description="Настройка уведомлений о верификации")
    async def verify_notify(
        self,
        interaction: nextcord.Interaction,
        activate: bool = nextcord.SlashOption(
            name="включена", description="Состояние уведомления о верификации"
        ),
        channel: nextcord.TextChannel = nextcord.SlashOption(
            name="канал_для_уведомления", description="Канал для отправки уведомления"
        ),
        phrases: str = nextcord.SlashOption(
            name="роли",
            description="Написанные через точку-запятую фразы для уведомления",
            required=False,
        ),
    ):
        await interaction.response.defer(ephemeral=True)
        guild_info = self.bot.database.get_guild_info(interaction.guild.id)
        if not activate:
            guild_info.verify_notify = False
            await interaction.followup.send(f"Уведомления о верификации деактивированы")
        else:
            phrases = phrases.split(";")
            guild_info.verify_notify = True
            guild_info.verify_notify_channel = channel.id
            guild_info.verify_notify_phrases = phrases
            await interaction.followup.send(
                f"Уведомления о верификации активированы в канале {channel.mention}"
            )
        await self.bot.database.session.commit()


def setup(bot):
    bot.add_cog(Setup(bot))
