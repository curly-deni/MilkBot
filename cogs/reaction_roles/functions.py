import nextcord
from base.base_cog import MilkCog
from nextcord.ext import commands


class ReactionRoles(MilkCog, name="Reaction Roles"):
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

        if db_info.verify:
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
        for i in db_info.roles:
            emoji = i.split("#")[0]
            role = int(i.split("#")[1])
            roles_and_emojis[emoji] = role

        if not db_info.single_use:
            role = channel.guild.get_role(roles_and_emojis[str(payload.emoji)])
            if role is None:
                return
            try:
                await member.remove_roles(role, reason="ReactionRole")
            except:
                pass


def setup(bot):
    bot.add_cog(ReactionRoles(bot))
