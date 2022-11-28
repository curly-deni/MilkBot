import traceback
from random import choice
from typing import Optional

import nextcord
from base.base_cog import MilkCog
from nextcord.ext import commands, tasks
from nextcord.ext.commands import Context
from nextcord.utils import get

from .ui import SelectRole


class Moderation(MilkCog, name="Верификация"):
    """Верификация с помощью MilkBot"""

    COG_EMOJI: str = "✅"

    def __init__(self, bot):
        self.bot = bot
        self.check_mutes.start()
        self.required_permission = "moderator"

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
                await member.add_roles(role, reason="ReactionRole Verify")
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

        if not db_info.verify:
            return

        roles_and_emojis = {}
        for i in db_info.roles:
            emoji = i.split("#")[0]
            role = int(i.split("#")[1])
            roles_and_emojis[emoji] = role

        role_set = set(roles_and_emojis.values())
        user_roles = {role.id for role in member.roles}
        if not list(user_roles & role_set):
            await set_role()
        await self.restore_roles(member)
        await message.remove_reaction(str(payload.emoji), member)

        guild_info = self.bot.database.get_guild_info(member.guild.id)
        if not guild_info.verify_notify:
            return

        try:
            channel = self.bot.get_channel(guild_info.verify_notify_channel)
            phrase = (
                choice(guild_info.verify_notify_phrases)
                .replace("user_mention", member.mention)
                .replace("user_name", member.name)
            )
            await channel.send(phrase)
        except:
            ...

    async def restore_roles(self, member: nextcord.Member):
        guild_info = self.bot.database.get_guild_info(member.guild.id)

        if not guild_info.restore_roles:
            return

        user_info = self.bot.database.get_user_roles(member.id, member.guild.id)
        if user_info is None or not user_info.roles:
            return

        current_roles: list[int] = [
            role.id for role in member.roles if role != member.guild.default_role
        ]
        roles: list[nextcord.Role] = [
            member.guild.get_role(role_id)
            for role_id in user_info.roles
            if member.guild.get_role(role_id) is not None
            and role_id not in current_roles
            and role_id not in guild_info.admin_roles
            and role_id not in guild_info.moderator_roles
            and role_id not in guild_info.editor_roles
        ]
        if roles:
            await member.add_roles(*roles)

    # check database for ended mutes
    @tasks.loop(seconds=10)
    async def check_mutes(self):

        for guild in self.bot.guilds:
            role: nextcord.Role = get(guild.roles, name="Muted")

            try:
                texts: list = self.bot.database.get_expired_text_mutes(guild.id)
                voices = self.bot.database.get_expired_voice_mutes(guild.id)

                # check voice mutes
                for member in texts:
                    user: nextcord.Member = await guild.fetch_member(member.id)
                    try:
                        await user.remove_roles(role)
                        self.bot.database.del_text_mute(member.id, guild.id)
                    except:
                        continue

                # check voice mutes list
                for member in voices:
                    user: nextcord.Member = await guild.fetch_member(member.id)
                    try:
                        await user.edit(mute=False)
                        self.bot.database.del_voice_mute(member.id, guild.id)
                    except:
                        continue
            except:
                continue

    async def restore_roles(self, member: nextcord.Member):
        user_info = self.bot.database.get_user_roles(member.id, member.guild.id)
        if user_info is None or not user_info.roles:
            return

        current_roles: list[int] = [
            role.id for role in member.roles if role != member.guild.default_role
        ]
        roles: list[nextcord.Role] = [
            member.guild.get_role(role_id)
            for role_id in user_info.roles
            if member.guild.get_role(role_id) is not None
            and role_id not in current_roles
        ]
        if roles:
            try:
                await member.add_roles(*roles)
            except nextcord.Forbidden:
                pass

    async def verify(
        self, container: Context | nextcord.Interaction, user: nextcord.Member
    ):
        async def send_message(
            content=None, message_view=nextcord.utils.MISSING
        ) -> nextcord.Message:
            if isinstance(container, Context):
                message = await container.send(content=content, view=message_view)
            else:
                message = await container.followup.send(
                    content=content, view=message_view
                )
            return message

        guild_info = self.bot.database.get_guild_info(container.guild.id)
        if isinstance(container, Context):
            author = container.author
        else:
            author = container.user

        if not guild_info.verify:
            return await send_message(
                f"{self.bot.user.name} не отвечает за верификацию на данном сервере!"
            )

        member_roles = [role for role in user.roles if role != user.guild.default_role]
        if member_roles:
            return await send_message(f"Пользователь **{user.name}** уже верифицирован")

        roles = []
        for role_id in guild_info.verify_roles:
            try:
                role = container.guild.get_role(role_id)
                if role is not None:
                    roles.append(role)
            except:
                continue

        if not roles:
            return await send_message(f"Не найдено роли для верификации")

        if len(roles) != 1:
            view = SelectRole(author, roles)
            message = await send_message(
                content="Выберите роль для верификации", message_view=view
            )
            view.message = message
            await view.wait()

            if not isinstance(view.value, nextcord.Role):
                return await send_message(f"Не выбрана роль для верификации")
            role = view.value
        else:
            role = roles[0]

        try:
            await user.add_roles(role)
        except Exception as error:
            return await send_message(
                "Возникла ошибка:\n" + "\n".join(traceback.format_exception(error))
            )

        await send_message(
            f"Роль **{role.name}** успешно выдана пользователю **{user.name}**"
        )
        if not guild_info.verify_notify:
            return

        await self.restore_roles(user)

        try:
            channel = self.bot.get_channel(guild_info.verify_notify_channel)
            phrase = (
                choice(guild_info.verify_notify_phrases)
                .replace("user_mention", user.mention)
                .replace("user_name", user.name)
            )
            await channel.send(phrase)
        except Exception as error:
            return await send_message(
                "При отправке уведомления в чат возникла ошибка:\n"
                + "\n".join(traceback.format_exception(error))
            )

    @MilkCog.slash_command(
        name="verify",
        description="Верификация новых пользователей",
    )
    async def verify_slash(
        self,
        interaction: nextcord.Interaction,
        user: Optional[nextcord.Member] = nextcord.SlashOption(
            name="пользователь", required=True
        ),
    ):
        await interaction.response.defer()
        await self.verify(interaction, user)

    @MilkCog.message_command(
        name="verify",
        brief="Верификация новых пользователей",
        aliases=[
            "give_role" "giverole",
            "permit",
            "разрешить",
            "пропустить",
        ],
    )
    async def verify_message(self, ctx: Context, user: nextcord.Member):
        await ctx.trigger_typing()
        await self.verify(ctx, user)

    @verify_message.error
    async def give_role_error(self, ctx: Context, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Некорректное упоминание")


def setup(bot):
    bot.add_cog(Moderation(bot))
