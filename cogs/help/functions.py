from dataclasses import dataclass
from typing import Optional

import nextcord
from base.base_cog import MilkCog
from modules.checkers import (
    check_admin_permissions,
    check_editor_permission,
    check_moderator_permission,
)
from nextcord.ext import commands
from nextcord.ext.commands import Context

from .ui import HelpPaginatior


@dataclass
class HelpPaginationElement:
    emoji: Optional[str]
    name: str
    description: str
    embed: nextcord.Embed


@dataclass
class MilkSlashSubcommand:
    name: str
    command_type: str
    brief: str
    description: str
    required_permission: str
    aliases: list


class HelpCog(MilkCog, name="Помощь"):
    """Отображает помощь"""

    COG_EMOJI: str = "❔"

    def __init__(self, bot):
        self.bot = bot

    @MilkCog.slash_command(name="help", description="Вывод справки по боту")
    async def help_slash(self, interaction: nextcord.Interaction):
        await interaction.response.defer(ephemeral=True)
        return await self.help(interaction)

    @MilkCog.message_command(
        name="help", brief="Вывод справки", aliases=["помощь", "помогите", "хелп"]
    )
    async def help_message(self, ctx: Context):
        return await self.help(ctx)

    async def help(self, container: Context | nextcord.Interaction):
        is_user_admin = await check_admin_permissions(container, self.bot)
        is_user_moderator = await check_moderator_permission(container, self.bot)
        is_user_editor = await check_editor_permission(container, self.bot)

        try:
            prefix = self.bot.prefixes[container.guild.id]
        except:
            prefix = "="

        cogs_commands = self.bot.cogs_commands_dict.copy()
        cogs_obj = self.bot.cogs_obj_dict.copy()

        del_cogs_commands = []
        for cog_name, cog_commands in cogs_commands.items():
            cog: MilkCog = cogs_obj.get(cog_name, "Invalid")
            if not isinstance(cog, str):
                name = cog.qualified_name
                emoji = getattr(cog, "COG_EMOJI", "")
            else:
                name = "Invalid"
                emoji = ""
            if name == "Помощь":
                del_cogs_commands.append(cog_name)
                continue
            del_cog_commands = []
            add_cog_commands = []
            for command in cog_commands:

                if command.required_permission in ["", None]:
                    may_use = True
                elif is_user_editor and command.required_permission == "editor":
                    may_use = True
                elif is_user_moderator and command.required_permission == "moderator":
                    may_use = True
                elif is_user_admin and command.required_permission == "admin":
                    may_use = True
                else:
                    may_use = False

                try:
                    if may_use and command.checks:
                        try:
                            may_use = await nextcord.utils.async_all(
                                predicate(container) for predicate in command.checks
                            )
                        except:
                            may_use = False
                except:
                    continue

                if command.only_at_guilds:
                    if container.guild.id in command.only_at_guilds:
                        guild_en = True
                    else:
                        guild_en = False
                else:
                    if container.guild.id in command.ignore_guilds:
                        guild_en = False
                    else:
                        guild_en = True
                if not may_use or not guild_en:
                    del_cog_commands.append(command)
                else:
                    if command.command_type == "slash":
                        if command.children != {}:
                            del_cog_commands.append(command)
                        for child in command.children.values():
                            if child.children == {}:
                                add_cog_commands.append(
                                    MilkSlashSubcommand(
                                        name=f"{command.name} {child.name}",
                                        brief=child.description,
                                        description=child.description,
                                        required_permission=command.required_permission,
                                        command_type="slash",
                                        aliases=[],
                                    )
                                )
                            else:
                                for another_child in child.children.values():
                                    add_cog_commands.append(
                                        MilkSlashSubcommand(
                                            name=f"{command.name} {child.name} {another_child.name}",
                                            brief=another_child.description,
                                            description=another_child.description,
                                            required_permission=command.required_permission,
                                            command_type="slash",
                                            aliases=[],
                                        )
                                    )

            for el in del_cog_commands:
                cog_commands.remove(el)
            cog_commands.extend(add_cog_commands)
            if not cog_commands:
                del_cogs_commands.append(cog_name)
        for el in del_cogs_commands:
            cogs_commands.pop(el)

        guild_info = self.bot.database.get_guild_info(container.guild.id)

        admin_roles = (
            ", ".join(
                [
                    container.guild.get_role(role_id).mention
                    for role_id in guild_info.admin_roles
                    if container.guild.get_role(role_id) is not None
                ]
            )
            if guild_info.admin_roles
            else ""
        )

        moderator_roles = (
            ", ".join(
                [
                    container.guild.get_role(role_id).mention
                    for role_id in guild_info.moderator_roles
                    if container.guild.get_role(role_id) is not None
                ]
            )
            if guild_info.moderator_roles
            else ""
        )

        editor_roles = (
            ", ".join(
                [
                    container.guild.get_role(role_id).mention
                    for role_id in guild_info.editor_roles
                    if container.guild.get_role(role_id) is not None
                ]
            )
            if guild_info.editor_roles
            else ""
        )

        roles = {
            "admin": (
                "Необходимы права администратора (Discord) либо одна из ролей: "
                + admin_roles
                if admin_roles != ""
                else "Необходимы права администратора (Discord)"
            ),
            "moderator": (
                "Необходимы права администратора (Discord) либо одна из ролей: "
                + admin_roles
                + moderator_roles
                if (admin_roles + moderator_roles) != ""
                else "Необходимы права администратора (Discord)"
            ),
            "editor": (
                f"Необходимы права администратора (Discord) либо одна из ролей: "
                + admin_roles
                + moderator_roles
                + editor_roles
                if (admin_roles + moderator_roles + editor_roles) != ""
                else "Необходимы права администратора (Discord)"
            ),
            "": "",
            None: "",
        }

        embeds = []
        main_embed_fields = []
        color = nextcord.Colour.random()
        for cog_name, cog_commands in cogs_commands.items():
            cog: MilkCog = cogs_obj.get(cog_name, "Invalid")
            if not isinstance(cog, str):
                name = cog.qualified_name
                description = cog.description
                emoji = getattr(cog, "COG_EMOJI", "")
            else:
                name = "Invalid"
                description = ""
                emoji = ""

            command_name_list = [
                f'`{"/" if command.command_type == "slash" else prefix}{command.name}`'
                for command in cog_commands
            ]
            main_embed_fields.append(
                [
                    name,
                    emoji,
                    (f"*{description}*\n" if description != "" else description)
                    + " ".join(command_name_list),
                ]
            )

            embed = nextcord.Embed(
                title=emoji + name,
                colour=color,
                description=(
                    f"*{description}*\n" if description != "" else description
                ),
            )
            embed_fields = []
            for command in cog_commands:
                command_name = command.name
                command_brief = (
                    (command.brief + "\n")
                    if command.brief not in ["", None]
                    else "Описание отсутствует\n"
                )
                command_description = (
                    (command.description + "\n")
                    if command.description not in ["", "No description provided.", None]
                    and command.brief != command.description
                    else ""
                )
                command_permission = roles[command.required_permission]
                command_prefix = "/" if command.command_type == "slash" else prefix
                if command.aliases:
                    command_aliases = (
                        f' [{", ".join([prefix + alias for alias in command.aliases])}]'
                    )
                else:
                    command_aliases = ""

                embed_fields.append(
                    [
                        command_name.replace("_", "\_"),
                        command_brief,
                        command_description,
                        command_permission,
                        command_prefix,
                        command_aliases.replace("_", "\_"),
                    ]
                )
            embed_fields.sort(key=lambda field: field[0])
            for field in embed_fields:
                embed.add_field(
                    name=field[4] + field[0] + field[5],
                    value=field[1] + field[2] + field[3],
                    inline=False,
                )
            embed.set_footer(
                text="В справке отображены только команды, которые вы можете использовать"
            )
            embeds.append(
                HelpPaginationElement(
                    emoji=emoji, name=name, description=description, embed=embed
                )
            )

        main_embed_fields.sort(key=lambda field: field[0])
        embed = nextcord.Embed(title="Справка по командам бота", colour=color)
        for field in main_embed_fields:
            embed.add_field(name=field[1] + field[0], value=field[2], inline=False)
        embed.set_footer(
            text="В справке отображены только команды, которые вы можете использовать"
        )
        embeds.append(
            HelpPaginationElement(
                emoji="🏠",
                name="Главная страница",
                description="Список всех команд",
                embed=embed,
            )
        )
        if isinstance(container, Context):
            message = await container.send(embed=embed)
            view = HelpPaginatior(message, container.author, embeds)
        else:
            message = await container.followup.send(embed=embed)
            view = HelpPaginatior(message, container.user, embeds)
        await message.edit(view=view)


def setup(bot: commands.Bot):
    bot.add_cog(HelpCog(bot))
