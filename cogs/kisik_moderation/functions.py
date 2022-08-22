import nextcord
from nextcord.ext import commands
from nextcord.ext.commands import Context
from nextcord.utils import get
from modules.checkers import check_moderator_permission, app_check_moderator_permission

import random
from typing import Optional


class KisikModeration(commands.Cog, name="Модерация [Кисик]"):
    """Модерация с помощью бота"""

    COG_EMOJI: str = "👮"

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx: Context) -> bool:
        if ctx.guild is None:
            return True

        else:
            return check_moderator_permission(ctx) and ctx.message.guild.id in [
                876474448126050394,
                938461972448559116,
            ]

    @nextcord.slash_command(
        guild_ids=[], force_global=True, description="Выдача роли новичкам из причала"
    )
    async def permit(
        self,
        interaction: nextcord.Interaction,
        user: Optional[nextcord.Member] = nextcord.SlashOption(required=True),
    ):
        if interaction.guild is None:
            return await interaction.send("Вы на находитесь на сервере!")
        if interaction.guild.id != 876474448126050394:
            return await interaction.send("Данная функция отключена на сервере!")
        await interaction.response.defer(ephemeral=True)

        if not app_check_moderator_permission(interaction, self.bot):
            return await interaction.followup.send("Недостаточно прав!", ephemeral=True)

        roles: list = [
            876494696153743450,
            876483834672189481,
            876483833841721434,
            876483833250320465,
            876483832205963315,
            879220481675362375,
            879220494321205278,
        ]

        if any(role.id in roles for role in user.roles):
            return await interaction.followup.send(
                "Котик уже есть на кораблике. <:liss:950156995816751114>"
            )
        else:
            await user.add_roles(get(user.guild.roles, name="Хвостатый юнга"))
            await interaction.followup.send("✅")
            channel: nextcord.TextChannel = self.bot.get_channel(876474448126050397)
            responses: list[str] = [
                "Лапки {} вступили на борт!",
                "{} не зевай, хватай швабру!",
                "Новый котик {} появился на палубе!",
                "{} пришёл на запах свежей рыбы!",
                "Неожиданный улов. {} добро пожаловать на борт!",
                "{} пришел, чтобы увидеть дальние берега!",
            ]
            await channel.send(random.choice(responses).format(user.mention))

    @commands.command(
        brief="Выдача роли новичкам из причала",
        aliases=[
            "giverole",
            "permit",
            "разрешить",
            "пропустить",
            "Разрешить",
            "Пропустить",
        ],
    )
    async def give_role(self, ctx: Context, user: nextcord.Member):
        await ctx.trigger_typing()
        roles: list = [
            876494696153743450,
            876483834672189481,
            876483833841721434,
            876483833250320465,
            876483832205963315,
            879220481675362375,
            879220494321205278,
        ]

        if any(role.id in roles for role in user.roles):
            return await ctx.reply(
                "Котик уже есть на кораблике. <:liss:950156995816751114>"
            )
        else:
            await user.add_roles(get(user.guild.roles, name="Хвостатый юнга"))
            await ctx.message.add_reaction("✅")
            channel: nextcord.TextChannel = self.bot.get_channel(876474448126050397)
            responses: list[str] = [
                "Лапки {} вступили на борт!",
                "{} не зевай, хватай швабру!",
                "Новый котик {} появился на палубе!",
                "{} пришёл на запах свежей рыбы!",
                "Неожиданный улов. {} добро пожаловать на борт!",
                "{} пришел, чтобы увидеть дальние берега!",
            ]
            await channel.send(random.choice(responses).format(user.mention))

    @give_role.error
    async def give_role_error(self, ctx: Context, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(
                "Я не могу найти этого человека. <a:_cry:876789104094883842>"
            )


def setup(bot):
    bot.add_cog(KisikModeration(bot))
