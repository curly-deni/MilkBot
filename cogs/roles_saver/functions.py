from random import choice

import nextcord
from base.base_cog import MilkCog
from nextcord.ext import commands


class RolesSaver(MilkCog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_remove(self, member: nextcord.Member):
        guild_info = self.bot.database.get_guild_info(member.guild.id)

        if not guild_info.restore_roles:
            return

        roles = [
            role.id
            for role in member.roles
            if role != member.guild.default_role
            and role.id not in guild_info.admin_roles
            and role.id not in guild_info.moderator_roles
            and role.id not in guild_info.editor_roles
        ]
        if roles:
            self.bot.database.add_user_roles(member.id, member.guild.id, roles)

    @commands.Cog.listener()
    async def on_member_join(self, member: nextcord.Member):
        guild_info = self.bot.database.get_guild_info(member.guild.id)

        if not guild_info.restore_roles:
            return

        if guild_info.need_verify and member.id != self.bot.settings["owner_id"]:
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

        try:
            channel = self.bot.get_channel(guild_info.verify_notify_channel)
            phrase = (
                choice(guild_info.verify_notify_phrases)
                .replace("user_mention", member.mention)
                .replace("user_name", member.name)
            )
            await channel.send(phrase)
        except:
            pass


def setup(bot):
    bot.add_cog(RolesSaver(bot))
