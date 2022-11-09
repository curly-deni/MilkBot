import nextcord
import traceback
from nextcord.ext import commands
from typing import Optional
from modules.checkers import check_moderator_permission
from .ui import NewReactionRolesSetup, ExReactionRolesSetup


class ReactionRoles(commands.Cog, name="Reaction Roles"):
    """Настройка сообщений для выдачи ролей по реакциям"""

    COG_EMOJI: str = "🧰"

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: nextcord.RawReactionActionEvent):
        async def set_role():
            role = channel.guild.get_role(roles_and_emojis[str(payload.emoji)])
            if role is None:
                await message.remove_reaction(str(payload.emoji), member)
                return

            if role in member.roles:
                return

            try:
                await member.add_roles(role, reason="ReactionRole")
            except:
                await message.remove_reaction(str(payload.emoji), member)

        channel: nextcord.TextChannel = self.bot.get_channel(payload.channel_id)
        message: nextcord.Message = await channel.fetch_message(payload.message_id)
        member: nextcord.Member = payload.member
        if member.bot:
            return

        db_info = self.bot.database.get_reaction_roles_info(message.id, channel.id)
        if db_info is None:
            return

        roles_and_emojis = {}
        # role_list = []
        for i in db_info.roles:
            emoji = i.split("#")[0]
            role = int(i.split("#")[1])
            # role_list.append(role)

            roles_and_emojis[emoji] = role

        if db_info.single_use:
            role_set = set(roles_and_emojis.values())
            user_roles = {role.id for role in member.roles}
            if not list(user_roles & role_set):
                await set_role()
            await message.remove_reaction(str(payload.emoji), member)
            return

        elif db_info.unique:
            await set_role()

            for reaction in message.reactions:
                if reaction.emoji != str(payload.emoji):
                    try:
                        await message.remove_reaction(reaction.emoji, member)
                    except:
                        pass
                    try:
                        role = channel.guild.get_role(roles_and_emojis[reaction.emoji])
                        await member.remove_roles(role)
                    except:
                        pass

            return
        else:
            await set_role()

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: nextcord.RawReactionActionEvent):

        channel: nextcord.TextChannel = self.bot.get_channel(payload.channel_id)
        member: nextcord.Member = channel.guild.get_member(payload.user_id)
        if member.bot:
            return

        db_info = self.bot.database.get_reaction_roles_info(
            payload.message_id, channel.id
        )
        if db_info is None:
            return

        roles_and_emojis = {}
        # role_list = []
        for i in db_info.roles:
            emoji = i.split("#")[0]
            role = int(i.split("#")[1])
            # role_list.append(role)

            roles_and_emojis[emoji] = role

        if not db_info.single_use:
            role = channel.guild.get_role(roles_and_emojis[str(payload.emoji)])
            if role is None:
                return
            try:
                await member.remove_roles(role, reason="ReactionRole")
            except:
                pass

    @commands.command(brief="Создание сообщения для выдачи роли по реакциям")
    @commands.check(check_moderator_permission)
    @commands.guild_only()
    async def rroles_create(self, ctx: nextcord.ext.commands.Context):
        view = NewReactionRolesSetup(ctx.author, self.bot)
        control_message = await ctx.send(view=view)
        preview_message = await ctx.send(embed=view.embed)
        view.control_message = control_message
        view.preview_message = preview_message
        view.original_channel = ctx.channel
        await view.wait()

    @commands.command(brief="Редактирование сообщения для выдачи роли по реакциям")
    @commands.check(check_moderator_permission)
    @commands.guild_only()
    async def rroles_edit(self, ctx: nextcord.ext.commands.Context):

        status_messages = []

        async def del_status():
            for i in status_messages:
                try:
                    await i.delete()
                except:
                    continue

        status_messages.append(await ctx.send("Введите ID чата, или упомяните его."))
        channel_id = await self.bot.wait_for(
            "message",
            check=lambda message: message.author == ctx.author
            and message.channel == ctx.channel,
        )
        channel_id.content = (
            channel_id.content.replace("#", "").replace("<", "").replace(">", "")
        )
        if not (channel_id.content).isdigit():
            await ctx.send("Некорректный ID")
            await del_status()
            return
        channel: Optional[nextcord.TextChannel] = self.bot.get_channel(
            int(channel_id.content)
        )
        if channel is None:
            await ctx.send(f"Не найден канал с ID {channel_id.content}")
            await del_status()
            return
        else:
            status_messages.append(
                await ctx.send(f"Выбран канал **{channel.name}** ({channel.id})")
            )

        status_messages.append(await ctx.send("Введите ID сообщения"))
        message_id = await self.bot.wait_for(
            "message",
            check=lambda message: message.author == ctx.author
            and message.channel == ctx.channel,
        )
        if not (message_id.content).isdigit():
            await ctx.send("Некорректный ID")
            await del_status()
            return
        message = await channel.fetch_message(int(message_id.content))
        if message is None:
            await ctx.send(f"Не найдено сообщение с ID {message_id.content}")
            await del_status()
            return
        else:
            status_messages.append(await ctx.send("Сообщение выбрано"))

        db_info = self.bot.database.get_reaction_roles_info(message.id, channel.id)
        if db_info is None:
            await ctx.send("В БД не обнаружено записей об этом сообщении")
            await del_status()
            return

        if ctx.author.id != db_info.author_id:
            await ctx.send(f"Вы не являетесь автором этого блока")
            await del_status()
            return

        view = ExReactionRolesSetup(ctx.author, self.bot, message, db_info)
        control_message = await ctx.send(view=view)
        content_message = (
            f"**Только одна выбранная роль:** {'Да' if view.unique else 'Нет'}\n"
            + f"**Однократное использование:** {'Да' if view.single_use else 'Нет'}"
        )
        preview_message = await ctx.send(content=content_message, embed=view.embed)
        for emoji in view.reaction_and_roles:
            await preview_message.add_reaction(emoji)
        view.control_message = control_message
        view.preview_message = preview_message
        view.original_channel = ctx.channel
        await view.wait()
        await message_id.delete()
        await channel_id.delete()
        await del_status()

    @commands.command(brief="Удаление сообщения для выдачи роли по реакциям")
    @commands.check(check_moderator_permission)
    @commands.guild_only()
    async def rroles_delete(self, ctx: nextcord.ext.commands.Context):

        status_messages = []

        async def del_status():
            for i in status_messages:
                try:
                    await i.delete()
                except:
                    continue

        status_messages.append(await ctx.send("Введите ID чата, или упомяните его."))
        channel_id = await self.bot.wait_for(
            "message",
            check=lambda message: message.author == ctx.author
            and message.channel == ctx.channel,
        )
        channel_id.content = (
            channel_id.content.replace("#", "").replace("<", "").replace(">", "")
        )
        if not (channel_id.content).isdigit():
            await ctx.send("Некорректный ID")
            await del_status()
            return
        channel: Optional[nextcord.TextChannel] = self.bot.get_channel(
            int(channel_id.content)
        )
        if channel is None:
            await ctx.send(f"Не найден канал с ID {channel_id.content}")
            await del_status()
            return
        else:
            status_messages.append(
                await ctx.send(f"Выбран канал **{channel.name}** ({channel.id})")
            )

        status_messages.append(await ctx.send("Введите ID сообщения"))
        message_id = await self.bot.wait_for(
            "message",
            check=lambda message: message.author == ctx.author
            and message.channel == ctx.channel,
        )
        if not (message_id.content).isdigit():
            await ctx.send("Некорректный ID")
            await del_status()
            return
        message = await channel.fetch_message(int(message_id.content))
        if message is None:
            await ctx.send(f"Не найдено сообщение с ID {message_id.content}")
            await del_status()
            return
        else:
            status_messages.append(await ctx.send("Сообщение выбрано"))

        db_info = self.bot.database.get_reaction_roles_info(message.id, channel.id)
        if db_info is None:
            await ctx.send("В БД не обнаружено записей об этом сообщении")
            await del_status()
            return

        await message.clear_reactions()
        self.bot.database.delete_reaction_roles_info(message.id, channel.id)
        await ctx.send("ReactionRoles успешно удалён")
        await channel_id.delete()
        await message_id.delete()
        await del_status()


def setup(bot):
    bot.add_cog(ReactionRoles(bot))
