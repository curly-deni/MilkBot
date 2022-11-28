import datetime
from typing import Optional, Union

import modules.database
import nextcord
from base.base_cog import MilkCog
from modules.checkers import app_check_editor_permission
from modules.paginator import Paginator
from modules.utils import list_split
from nextcord.ext.commands import Context
from nextcord.utils import get
from sqlalchemy import desc


class StatViewer(MilkCog, name="Статистика"):
    """Статистика пользователей сервера"""

    COG_EMOJI: str = "📓"

    def __init__(self, bot):
        self.bot = bot
        self.ignore_guilds = [876474448126050394]

    def cog_check(self, ctx: Context) -> bool:
        if ctx.guild is None:
            return True
        else:
            return ctx.message.guild.id != 876474448126050394

    @MilkCog.slash_command()
    async def guild(self, interaction: nextcord.Interaction):
        ...

    @guild.subcommand(description="Статистика пользователя")
    async def rank(
        self,
        interaction: nextcord.Interaction,
        user: Optional[nextcord.Member] = nextcord.SlashOption(
            name="пользователь", description="пользователь", required=False
        ),
    ):
        await interaction.response.defer()

        if not isinstance(user, nextcord.Member):
            user = interaction.user

        user_info: modules.database.GuildsStatistics = (
            self.bot.database.get_member_statistics(user.id, interaction.guild.id)
        )

        embed: nextcord.Embed = nextcord.Embed(
            timestamp=datetime.datetime.now(),
            description=f"""*{user_info.citation if user_info.citation is not None and user_info.citation != "" else "установка цитаты по команде /quote"}*\n
**Дата вступления на сервер:** {nextcord.utils.format_dt(user.joined_at, 'f')}\n""",
            colour=nextcord.Colour.random(),
        )

        if user.roles:
            embed.description += (
                "**Роли пользователя:** "
                + ", ".join(
                    [
                        role.name
                        for role in user.roles
                        if role.id != user.guild.default_role.id
                    ]
                )
                + "\n"
            )

        embed.title = f"Статистика пользователя {user.display_name}"
        if user.avatar:
            embed.set_thumbnail(url=user.avatar.url)
        else:
            embed.set_thumbnail(
                url=f"https://cdn.discordapp.com/embed/avatars/{int(user.discriminator) % 5}.png",
            )

        if interaction.guild.icon:
            embed.set_author(
                name=interaction.guild.name, icon_url=interaction.guild.icon.url
            )
        else:
            embed.set_author(name=interaction.guild.name)

        peoples_undefined: list = self.bot.database.get_all_members_statistics(
            interaction.guild.id
        )  # .sort(key=lambda people: people.xp)
        peoples: list[int] = []
        for people in peoples_undefined:
            member = get(interaction.guild.members, id=people.id)
            if member is not None:
                peoples.append(member.id)

        embed.add_field(name="Валюты", value=f"✨ {user_info.gems}\n🪙 {user_info.coins}")
        embed.add_field(
            name="Статистика",
            value=f"**Уровень:** {user_info.lvl}\n**Опыт:** {user_info.xp}\n**Место в топе:** {peoples.index(user.id)+1}",
        )

        voice_str = ""
        if user_info.voice_time is not None:
            hours: str = str(user_info.voice_time // 3600)
            minutes: Union[int, str] = (user_info.voice_time % 3600) // 60
            if minutes < 10:
                minutes = "0" + str(minutes)
            seconds: Union[int, str] = (user_info.voice_time % 3600) % 60
            if seconds < 10:
                seconds = "0" + str(seconds)

            if hours == "0":
                voice_str: str = f"\n:microphone: {minutes}:{seconds}"
            else:
                voice_str: str = f"\n:microphone: {hours}:{minutes}:{seconds}"

        embed.add_field(
            name="Активность", value=f":cookie: {user_info.cookies}{voice_str}"
        )

        await interaction.followup.send(embed=embed)

    @guild.subcommand(description="Топ пользователей сервера")
    async def leaders(self, interaction: nextcord.Interaction):
        await interaction.response.defer(ephemeral=True)

        peoples_undefined: list = self.bot.database.get_all_members_statistics(
            interaction.guild.id
        )
        peoples: list[list] = []

        for people in peoples_undefined:
            member: Optional[nextcord.Member] = interaction.guild.get_member(people.id)
            if member is not None:
                if not member.bot:
                    peoples.append([member, people])

        peoples = list_split(peoples)

        embs: list[nextcord.Embed] = []
        for page, people_list in enumerate(peoples):
            emb = nextcord.Embed(title=f"Топ пользователей | {interaction.guild.name}")
            emb.colour = nextcord.Colour.green()
            try:
                emb.set_thumbnail(url=interaction.guild.icon.url)
            except:
                pass

            for idx, items in enumerate(people_list):
                if items[1].lvl is not None:
                    strx = f"**Уровень:** {items[1].lvl} | "
                else:
                    strx = f"**Уровень:** 0 | "

                if items[1].xp is not None:
                    strx += f"**Опыт:** {items[1].xp} | "
                else:
                    strx += f"**Опыт:** 0 | "

                if items[1].cookies is not None:
                    if items[1].cookies != 0:
                        strx += f":cookie: {items[1].cookies} | "

                if items[1].gems is not None:
                    if items[1].gems != 0:
                        strx += f":sparkles: {items[1].gems} | "

                if items[1].coins is not None:
                    if items[1].coins != 0:
                        strx += f":coin: {items[1].coins} | "

                if items[1].voice_time is not None:
                    if items[1].voice_time != 0:
                        hours: str = str(items[1].voice_time // 3600)
                        minutes: Union[int, str] = (items[1].voice_time % 3600) // 60
                        if minutes < 10:
                            minutes = "0" + str(minutes)
                        seconds: Union[int, str] = (items[1].voice_time % 3600) % 60
                        if seconds < 10:
                            seconds = "0" + str(seconds)

                        if hours != "0":
                            strx += f":microphone: {hours}:{minutes}:{seconds}"
                        else:
                            strx += f":microphone: {minutes}:{seconds}"

                name: str = items[0].display_name

                emb.add_field(
                    name=f"{page*10 + idx + 1}. {name}",
                    value=strx,
                    inline=False,
                )
            if emb.fields:
                embs.append(emb)

        message: nextcord.Message = await interaction.send(embed=embs[0])

        paginator: Paginator = Paginator(
            message,
            embs,
            interaction.user,
            self.bot,
            footerpage=True,
            footerdatetime=False,
            footerboticon=True,
            timeout=180.0,
        )
        try:
            await paginator.start()
        except nextcord.errors.NotFound:
            pass

    @MilkCog.slash_command(permission="editor")
    async def gem(self, interaction: nextcord.Interaction):
        ...

    @gem.subcommand(description="Получение списка гемов у пользователей")
    async def list(self, interaction: nextcord.Interaction):
        await interaction.response.defer(ephemeral=True)

        if not app_check_editor_permission(interaction, self.bot):
            return await interaction.followup.send("Недостаточно прав!", ephemeral=True)

        embed: nextcord.Embed = nextcord.Embed(
            title="Cтатистика по гемам",
            colour=nextcord.Colour.random(),
            timestamp=datetime.datetime.now(),
            description="",
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

        peoples_undefined: list = (
            self.bot.database.session.query(modules.database.GuildsStatistics)
            .filter(modules.database.GuildsStatistics.guild_id == interaction.guild.id)
            .order_by(desc(modules.database.GuildsStatistics.gems))
        )
        if peoples_undefined:
            for people in peoples_undefined:
                member: Optional[nextcord.Member] = interaction.guild.get_member(
                    people.id
                )
                if member is not None and people.gems > 0:
                    embed.description += (
                        f"**{member.display_name}** - {people.gems} :sparkles:\n"
                    )

        await interaction.followup.send(embed=embed)

    @gem.subcommand(description="Увеличение числа гемов пользователя")
    async def add(
        self,
        interaction: nextcord.Interaction,
        user: Optional[nextcord.Member] = nextcord.SlashOption(
            name="пользователь", required=True
        ),
        count: Optional[int] = nextcord.SlashOption(name="количество", required=True),
    ):
        await interaction.response.defer(ephemeral=True)

        self.bot.database.add_gems(
            id=user.id, guild_id=interaction.guild.id, coins=count
        )
        await interaction.followup.send(f"{interaction.user.mention}, изменено!")

    @guild.subcommand(description="Установка цитаты")
    async def quote(
        self,
        interaction: nextcord.Interaction,
        quote: Optional[str] = nextcord.SlashOption(name="цитата", required=True),
    ):
        await interaction.response.defer(ephemeral=True)

        member_info: modules.database.GuildsStatistics = (
            self.bot.database.get_member_statistics(
                interaction.user.id, interaction.guild.id
            )
        )
        member_info.citation = quote
        self.bot.database.session.commit()
        await interaction.followup.send(
            f"{interaction.user.mention}, успешно заменено!"
        )


def setup(bot):
    bot.add_cog(StatViewer(bot))
