from typing import Optional

import nextcord
from base.base_cog import MilkCog
from nextcord.ext import commands


class ShibuRoomControl(MilkCog, name="Контроль ролей для комнаты Shibu"):
    """Выдача и изъятие ролей для приватного канала Shibu"""

    COG_EMOJI: str = "⚰️"

    def __init__(self, bot):
        self.bot = bot
        self.only_at_guilds = [570998496178470923]

    @MilkCog.message_command(
        name="коронация", brief="Выдача роли S.W.A.G. для приватного канала Shibu"
    )
    @commands.has_any_role("Adm", "sugar mommy")
    async def shibu_room_add_role(
        self, ctx: nextcord.ext.commands.Context, user: Optional[nextcord.Member] = None
    ):
        await ctx.trigger_typing()

        if not isinstance(user, nextcord.Member):
            return await ctx.send(
                f"{ctx.author.mention}, вы не указали человека для выдачи роли!"
            )

        role: Optional[nextcord.Role] = ctx.guild.get_role(928209702242902016)

        try:
            await user.add_roles(role)
            await ctx.send(
                f"{ctx.author.mention}, успешно выдана роль **{role.name}** пользователю {user.mention}"
            )
        except:
            return await ctx.send("Ошибка при выдаче роли! Попробуйте снова...")

    @MilkCog.message_command(
        name="казнь", brief="Изъятие роли S.W.A.G. для приватного канала Shibu"
    )
    @commands.has_any_role("Adm", "sugar mommy")
    async def shibu_room_del_role(
        self, ctx: nextcord.ext.commands.Context, user: Optional[nextcord.Member] = None
    ):
        await ctx.trigger_typing()

        if not isinstance(user, nextcord.Member):
            return await ctx.send(
                f"{ctx.author.mention}, вы не указали человека для изъятия роли!"
            )

        role: Optional[nextcord.Role] = ctx.guild.get_role(928209702242902016)

        if role not in user.roles:
            return await ctx.send(
                f"{ctx.author.mention}, у пользователя {user.mention} нет роли {role.name}"
            )

        try:
            await user.remove_roles(role)
            await ctx.send(
                f"{ctx.author.mention}, успешно убрана роль **{role.name}** у пользователя {user.mention}"
            )
        except:
            return await ctx.send("Ошибка при изъятии роли! Попробуйте снова...")


def setup(bot):
    bot.add_cog(ShibuRoomControl(bot))
