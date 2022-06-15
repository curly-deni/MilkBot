import nextcord
from nextcord.ext import commands
from nextcord.utils import get

# for log
from datetime import datetime

# buttons
import database
from .actions import ControlButtons


class Voice(commands.Cog, name="Приватные голосовые каналы"):
    """Создание и настройка приватных голосовых каналов"""

    COG_EMOJI: str = "📞"

    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Обновить сообщение")
    @commands.guild_only()
    async def войс_сообщение(self, ctx: commands.Context):

        if ctx.author.voice is not None:

            if ctx.author.voice.channel.permissions_for(ctx.author).manage_channels:

                channel_info: database.VoiceChannels = (
                    self.bot.database.get_voice_channel(
                        ctx.author.voice.channel.id, ctx.guild.id
                    )
                )

                channel: nextcord.TextChannel = self.bot.get_channel(
                    channel_info.text_id
                )
                message: nextcord.Message = await channel.fetch_message(
                    channel_info.message_id
                )

                buttons = ControlButtons(self.bot)

                await message.edit(view=buttons)
                await ctx.send(f"{ctx.author.mention}, сообщение обновлено!")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):

        guild: database.GuildsSetiings = self.bot.database.get_guild_info(
            member.guild.id
        )

        if before.channel is not None and after.channel is not None:
            if before.channel.id == after.channel.id:
                return False

        try:
            check_in_generator = after.channel.id == guild.voice_channel_generator
            check_in_private = (
                after.channel.category.id == guild.voice_channel_category
                and after.channel.id != guild.voice_channel_generator
            )
        except:
            check_in_generator = False
            check_in_private = False

        try:
            check_out_private = (
                before.channel.category.id == guild.voice_channel_category
                and before.channel.id != guild.voice_channel_generator
            )
        except:
            check_out_private = False
            pass

        if check_in_private:
            await self.in_private(member, after)

        if check_out_private:
            await self.out_private(member, before)

        if check_in_generator:
            await self.create_new_channel(member, guild.voice_channel_category)

    async def create_new_channel(
        self, member: nextcord.Member, private_category: int
    ) -> None:

        category: nextcord.CategoryChannel = get(
            member.guild.categories, id=private_category
        )

        # create voice channel

        channel_settings: database.VoiceChannelsSettings = (
            self.bot.database.get_voice_channel_settings(member.id, member.guild.id)
        )

        voice_channel: nextcord.VoiceChannel = await category.create_voice_channel(
            name=(
                channel_settings.name
                if channel_settings.name is not None and channel_settings.name != ""
                else member.display_name
            ),
            bitrate=channel_settings.bitrate,
            user_limit=(
                channel_settings.limit if channel_settings.limit is not None else 0
            ),
        )

        await voice_channel.set_permissions(member.guild.default_role, connect=False)

        await voice_channel.set_permissions(
            member, manage_channels=True, connect=True, speak=True, view_channel=True
        )

        text_channel: nextcord.TextChannel = await category.create_text_channel(
            name=channel_settings.name
            if channel_settings.name is not None and channel_settings.name != ""
            else member.display_name
        )

        emb: nextcord.Embed = nextcord.Embed(
            description=f"Если бот не реагирует на нажатие кнопок, запустите команду {self.bot.database.get_guild_prefix(member.guild.id)}войс_сообщение",
            colour=nextcord.Colour.random(),
        )

        fields: list[list[str]] = [
            ["✏", "**Изменить название канала**"],
            ["🔒", "**Закрыть канал**"],
            ["👥", "**Ограничить количество пользователей**"],
            # ["🔧", "**Установить битрейт канала**"],
            ["🚪", "**Кикнуть пользователя**"],
            ["🔇", "**Замьютить пользователя**"],
            ["🔊", "**Размьютить пользователя**"],
            ["🏴", "**Забанить пользователя**"],
            ["🏳️", "**Разбанить пользователя**"],
            ["🕵️", "**Открыть канал для пользователя (для закрытых каналов)**"],
            ["👑", "**Передать права на канал**"],
        ]

        f0: str = ""
        for field in fields:
            f0 += f"> {field[0]} - {field[1]}\n"

        emb.add_field(name="Команды", value=f0[:-1], inline=False)

        emb.set_footer(text=f"Спасибо за использование {self.bot.user.name}.")

        emb.add_field(name="Создатель канала", value=member.mention)
        emb.add_field(name="Владелец канала", value=member.mention)
        emb.add_field(
            name="Статус канала",
            value=f'{"Открыт" if channel_settings.open else "Закрыт"}',
        )

        buttons = ControlButtons(self.bot)
        message: nextcord.Message = await text_channel.send(embed=emb, view=buttons)
        await message.pin()

        self.bot.database.add_voice_channel(
            id=voice_channel.id,
            guild_id=member.guild.id,
            text_id=text_channel.id,
            owner_id=member.id,
            message_id=message.id,
        )

        await text_channel.set_permissions(
            member.guild.default_role, view_channel=False
        )

        await text_channel.set_permissions(
            member,
            view_channel=True,
            manage_channels=True,
            read_messages=True,
            read_message_history=True,
            send_messages=True,
        )

        try:
            await member.move_to(voice_channel)
        except:
            await voice_channel.delete()
            await text_channel.delete()

        banned_ar: list[nextcord.Member] = []
        for user in channel_settings.banned:
            try:
                banned_ar.append(await member.guild.fetch_member(user))
            except:
                continue

        for user in banned_ar:
            await voice_channel.set_permissions(user, connect=False)

        opened_ar: list[nextcord.Member] = []
        for user in channel_settings.opened:
            try:
                opened_ar.append(await member.guild.fetch_member(user))
            except:
                continue

        for user in opened_ar:
            await voice_channel.set_permissions(user, connect=True, view_channel=True)

        muted_ar: list[nextcord.Member] = []
        for user in channel_settings.muted:
            try:
                muted_ar.append(await member.guild.fetch_member(user))
            except:
                continue

        for user in muted_ar:
            await voice_channel.set_permissions(user, speak=False)

        if channel_settings.open:
            await voice_channel.set_permissions(member.guild.default_role, connect=True)

    async def in_private(
        self, member: nextcord.Member, after: nextcord.VoiceState
    ) -> None:

        text_channel_id: int = self.bot.database.get_voice_channel(
            after.channel.id, after.channel.guild.id
        ).text_id
        if text_channel_id is not None:
            text_channel: nextcord.TextChannel = member.guild.get_channel(
                text_channel_id
            )
            try:
                if not text_channel.permissions_for(member).manage_channels:
                    await text_channel.set_permissions(
                        member,
                        view_channel=True,
                        read_messages=True,
                        read_message_history=True,
                        send_messages=True,
                    )

                else:
                    await text_channel.set_permissions(
                        member,
                        manage_channel=True,
                        view_channel=True,
                        read_messages=True,
                        read_message_history=True,
                        send_messages=True,
                    )
            except:
                pass

    async def out_private(self, member, before):
        try:
            await member.edit(mute=False)
        except:
            try:
                if not before.channel.permissions_for(member).speak:
                    self.bot.database.add_voice_mute(
                        id=member.id, guild_id=member.guild.id, time=datetime.now()
                    )
            except:
                pass

        if not before.channel.members:

            channel_info = self.bot.database.get_voice_channel(
                before.channel.id, before.channel.guild.id
            )

            if channel_info is not None:
                text_id = channel_info.text_id
                self.bot.database.delete_voice_channel(
                    before.channel.id, before.channel.guild.id
                )
            else:
                text_id = None

            await before.channel.delete()

            if text_id is not None:
                try:
                    text_channel = member.guild.get_channel(text_id)
                    await text_channel.delete()
                except:
                    pass

        else:
            channel_info = self.bot.database.get_voice_channel(
                before.channel.id, before.channel.guild.id
            )

            if channel_info is not None:
                text_id = channel_info.text_id
            else:
                text_id = None

            if text_id is not None:
                text_channel = member.guild.get_channel(text_id)
                try:
                    if not text_channel.permissions_for(member).manage_channels:
                        await text_channel.set_permissions(member, overwrite=None)
                    else:
                        await text_channel.set_permissions(member, overwrite=None)
                        await text_channel.set_permissions(member, manage_channels=True)
                except:
                    pass


def setup(bot):
    bot.add_cog(Voice(bot))
