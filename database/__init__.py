import sqlalchemy.engine
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import scoped_session, sessionmaker
from nextcord.ext import tasks
from datetime import datetime

from .table_classes import *

from typing import Union


def new_lvl(lvl) -> int:
    if lvl != 0:
        return (5 * lvl**2 + 50 * lvl + 100) + new_lvl(lvl - 1)
    else:
        return 5 * lvl**2 + 50 * lvl + 100


def count_new_lvl(lvl, xp) -> int:
    nxp = new_lvl(lvl)
    if xp > nxp:
        return count_new_lvl(lvl + 1, xp)
    else:
        return lvl


class Database:
    def __init__(self, uri: str, bot=None):
        self.__uri = uri
        self.bot = bot

        self.__engine: Union[sqlalchemy.engine.base.Engine, None] = None
        self.session: Union[sqlalchemy.orm.session.Session, None] = None

    @tasks.loop(seconds=120)
    async def reconnect(self):
        if isinstance(self.__engine, sqlalchemy.engine.base.Engine):
            self.session.close()
            self.__engine.dispose()

        self.__engine: sqlalchemy.engine.Engine = create_engine(self.__uri)
        self.__engine.execute("ROLLBACK")

        self.session: sqlalchemy.orm.Session = sessionmaker(bind=self.__engine)()

    # bot settings
    def get_bot_settings(self) -> BotSettings:
        return self.session.query(BotSettings).get(0)

    def get_bot_prefix(self) -> str:
        return self.get_bot_settings().base_prefix

    def get_tables(self) -> dict:
        bot_settings = self.get_bot_settings()
        return {
            "astral": bot_settings.base_astral_table,
            "embeds": bot_settings.base_embeds_table,
            "art": bot_settings.base_art_table,
        }

    def get_last_news_time(self) -> datetime:
        return self.get_bot_settings().shikimori_last_news_time

    def set_last_news_time(self, time: datetime) -> None:
        bot_settings = self.get_bot_settings()
        bot_settings.shikimori_last_news_time = time
        self.session.commit()

    # guild settings
    def get_guild_info(self, guild_id: int) -> GuildsSetiings:
        guild = self.session.query(GuildsSetiings).get(guild_id)
        if guild is None:
            self.__add_guild_info(guild_id)
            guild = self.session.query(GuildsSetiings).get(guild_id)
        return guild

    def __add_guild_info(self, guild_id: int) -> None:
        self.session.add(
            GuildsSetiings(
                id=guild_id,
                prefix=self.get_bot_prefix(),
                admin_roles=[],
                moderator_roles=[],
                editor_roles=[],
                embeds_table="",
                astral_table="",
                art_table="",
                astral_script="",
                disabled_functions=[],
                horo=False,
                horo_roles=[],
                horo_channels=[],
                neuralhoro=False,
                neuralhoro_roles=[],
                neuralhoro_channels=[],
                shikimori_news=False,
                shikimori_news_roles=[],
                shikimori_news_channels=[],
                shikimori_releases=False,
                shikimori_releases_roles=[],
                shikimori_releases_channels=[],
                voice_channel_generator=0,
                voice_channel_category=0,
            )
        )

    def get_stuff_roles(self, guild_id: int) -> dict:
        guild = self.get_guild_info(guild_id)
        return {
            "editor": guild.editor_roles,
            "moderator": guild.moderator_roles,
            "admin": guild.admin_roles,
        }

    def add_stuff_roles(
        self,
        guild_id: int,
        editor_roles: list[int] = [],
        moderator_roles: list[int] = [],
        admin_roles: list[int] = [],
    ) -> None:
        guild = self.get_guild_info(guild_id)

        guild.editor_roles += editor_roles
        guild.moderator_roles += moderator_roles
        guild.admin_roles += admin_roles

        self.session.commit()

    def remove_stuff_roles(
        self,
        guild_id: int,
        editor_roles: list[int] = [],
        moderator_roles: list[int] = [],
        admin_roles: list[int] = [],
    ) -> None:
        guild = self.get_guild_info(guild_id)
        for role in editor_roles:
            guild.editor_roles.remove(role)

        for role in moderator_roles:
            guild.moderator_roles.remove(role)

        for role in admin_roles:
            guild.admin_roles.remove(role)

        self.session.commit()

    def get_guild_prefix(self, guild_id: int) -> str:
        return self.get_guild_info(guild_id).prefix

    def set_guild_prefix(self, guild_id: int, prefix: str) -> None:
        guild = self.get_guild_info(guild_id)
        guild.prefix = prefix
        self.session.commit()

    def get_all_prefixes(self) -> dict:
        prefixes = {}
        for guild in self.session.query(GuildsSetiings).all():
            prefixes[guild.id] = guild.prefix
        return prefixes

    def set_voice_channels(self, guild_id: int, setting: dict) -> None:
        guild = self.get_guild_info(guild_id)
        guild.voice_channel_category = setting["category"]
        guild.voice_channel_generator = setting["generator"]
        self.session.commit()

    def get_horo(self, guild_id: int) -> dict:
        guild = self.get_guild_info(guild_id)
        return {
            "activated": guild.horo,
            "roles": guild.horo_roles,
            "channels": guild.horo_channels,
        }

    def get_shikimori_news(self, guild_id: int) -> dict:
        guild = self.get_guild_info(guild_id)
        return {
            "activated": guild.shikimori_news,
            "roles": guild.shikimori_news_roles,
            "channels": guild.shikimori_news_channels,
        }

    def get_shikimori_releases(self, guild_id: int) -> dict:
        guild = self.get_guild_info(guild_id)
        return {
            "activated": guild.shikimori_releases,
            "roles": guild.shikimori_releases_roles,
            "channels": guild.shikimori_releases_channels,
        }

    def set_horo(
        self,
        guild_id: int,
        status: bool,
        roles: list[int] = [],
        channels: list[int] = [],
    ) -> None:
        guild = self.get_guild_info(guild_id)
        guild.horo = status

        if roles:
            guild.horo_roles = roles

        if channels:
            guild.horo_channels = channels

        self.session.commit()

    def set_neural_horo(
        self,
        guild_id: int,
        status: bool,
        roles: list[int] = [],
        channels: list[int] = [],
    ) -> None:
        guild = self.get_guild_info(guild_id)
        guild.neuralhoro = status

        if roles:
            guild.neuralhoro_roles = roles

        if channels:
            guild.neuralhoro_channels = channels

        self.session.commit()

    def set_shikimori_news(
        self,
        guild_id: int,
        status: bool,
        roles: list[int] = [],
        channels: list[int] = [],
    ) -> None:
        guild = self.get_guild_info(guild_id)
        guild.shikimori_news = status

        if roles:
            guild.shikimori_news_roles = roles

        if channels:
            guild.shikimori_news_channels = channels

        self.session.commit()

    def set_shikimori_releases(
        self,
        guild_id: int,
        status: bool,
        roles: list[int] = [],
        channels: list[int] = [],
    ) -> None:
        guild = self.get_guild_info(guild_id)
        guild.shikimori_releases = status

        if roles:
            guild.shikimori_releases_roles = roles

        if channels:
            guild.shikimori_releases_channels = channels

        self.session.commit()

    def get_all_horo(self) -> list:
        returnable_list = []
        for guild in self.session.query(GuildsSetiings).all():
            for channel in guild.horo_channels:
                returnable_list.append([channel, guild.horo_roles])
        return returnable_list

    def get_neural_all_horo(self) -> list:
        returnable_list = []
        for guild in self.session.query(GuildsSetiings).all():
            for channel in guild.neuralhoro_channels:
                returnable_list.append([channel, guild.neuralhoro_roles])
        return returnable_list

    def get_all_shikimori_news(self) -> list:
        returnable_list = []
        for guild in self.session.query(GuildsSetiings).all():
            for channel in guild.shikimori_news_channels:
                returnable_list.append([channel, guild.shikimori_news_roles])
        return returnable_list

    def get_all_shikimori_releases(self) -> list:
        returnable_list = []
        for guild in self.session.query(GuildsSetiings).all():
            for channel in guild.shikimori_releases_channels:
                returnable_list.append([channel, guild.shikimori_releases_roles])
        return returnable_list

    # stat

    def get_member_statistics(self, id: int, guild_id: int) -> GuildsStatistics:
        member = self.session.query(GuildsStatistics).get([id, guild_id])
        if member is None:
            self.__add_member_statistics(id, guild_id)
            member = self.session.query(GuildsStatistics).get([id, guild_id])
        return member

    def get_all_members_statistics(self, guild_id: int) -> list[GuildsStatistics]:
        return (
            self.session.query(GuildsStatistics)
            .filter(GuildsStatistics.guild_id == guild_id)
            .order_by(desc(GuildsStatistics.xp))
        )

    def __add_member_statistics(self, id: int, guild_id: int) -> None:
        self.session.add(
            GuildsStatistics(
                id=id,
                guild_id=guild_id,
                xp=0,
                lvl=0,
                voice_time=0,
                cookies=0,
                coins=0,
                gems=0,
                citation="",
            )
        )
        self.session.commit()

    def add_coins(self, id: int, guild_id: int, coins: int) -> None:
        member = self.get_member_statistics(id, guild_id)
        member.coins += coins
        self.session.commit()

    def add_gems(self, id: int, guild_id: int, coins: int) -> None:
        member = self.get_member_statistics(id, guild_id)
        member.gems += coins
        self.session.commit()

    def add_xp(self, id: int, guild_id: int, xp: int) -> None:
        member = self.get_member_statistics(id, guild_id)
        new_lvl = count_new_lvl(member.lvl, member.xp + xp) - member.lvl
        if count_new_lvl(member.lvl, member.xp + xp) != member.lvl and new_lvl > 0:
            self.add_lvl(id, guild_id, new_lvl)
        member.xp += round(xp)
        self.session.commit()

    def add_lvl(self, id: int, guild_id: int, lvl: int):
        member = self.get_member_statistics(id, guild_id)
        member.lvl += lvl
        self.session.commit()

    def add_cookie(self, id: int, guild_id: int, cookies: int = 1):
        member = self.get_member_statistics(id, guild_id)
        member.cookies += cookies
        self.session.commit()

    def add_voice_time(self, id: int, guild_id: int, time: int):
        member = self.get_member_statistics(id, guild_id)
        member.voice_time += time
        self.session.commit()

    # shikimori

    def get_shikimori_profile(self, id: int, guild_id: int) -> ShikimoriProfiles:
        return self.session.query(ShikimoriProfiles).get([id, guild_id])

    # text mutes

    def get_expired_text_mutes(self, guild_id: int) -> list[TextMutes]:
        return self.session.query(TextMutes).filter(
            TextMutes.stop <= datetime.now() and TextMutes.guild_id == guild_id
        )

    def del_text_mute(self, id: int, guild_id: int) -> None:
        self.session.query(TextMutes).filter(
            TextMutes.id == id and TextMutes.guild_id == guild_id
        ).delete()

    def add_text_mute(self, id: int, guild_id: int, time: datetime) -> None:
        self.session.add(TextMutes(id=id, guild_id=guild_id, stop=time))

    # voice mutes

    def get_expired_voice_mutes(self, guild_id: int) -> list[VoiceMutes]:
        return self.session.query(VoiceMutes).filter(
            VoiceMutes.stop <= datetime.now() and VoiceMutes.guild_id == guild_id
        )

    def del_voice_mute(self, id: int, guild_id: int) -> None:
        self.session.query(VoiceMutes).filter(
            VoiceMutes.id == id and VoiceMutes.guild_id == guild_id
        ).delete()

    def add_voice_mute(self, id: int, guild_id: int, time: datetime) -> None:
        self.session.add(VoiceMutes(id=id, guild_id=guild_id, stop=time))

    # voice channels settings

    def get_voice_channel_settings(
        self, id: int, guild_id: int
    ) -> VoiceChannelsSettings:
        channel = self.session.query(VoiceChannelsSettings).get([id, guild_id])
        if channel is None:
            self.__add_voice_channel_settings(id, guild_id)
            channel = self.session.query(VoiceChannelsSettings).get([id, guild_id])
        return channel

    def __add_voice_channel_settings(self, id: int, guild_id: int) -> None:
        self.session.add(
            VoiceChannelsSettings(
                id=id,
                guild_id=guild_id,
                bitrate=64000,
                limit=0,
                open=True,
                banned=[],
                muted=[],
                opened=[],
            )
        )

    def set_voice_channel_name(self, id: int, guild_id: int, name: str) -> None:
        channel = self.get_voice_channel_settings(id, guild_id)
        channel.name = name
        self.session.commit()

    def set_voice_channel_limit(self, id: int, guild_id: int, limit: int) -> None:
        channel = self.get_voice_channel_settings(id, guild_id)
        channel.limit = limit
        self.session.commit()

    def set_voice_channel_bitrate(self, id: int, guild_id: int, bitrate: int) -> None:
        channel = self.get_voice_channel_settings(id, guild_id)
        channel.bitrate = bitrate
        self.session.commit()

    def add_banned(self, id: int, guild_id: int, user: int) -> None:
        channel = self.get_voice_channel_settings(id, guild_id)
        channel.banned.append(user)
        self.session.commit()

    def remove_banned(self, id: int, guild_id: int, user: int) -> None:
        channel = self.get_voice_channel_settings(id, guild_id)
        channel.banned.remove(user)
        self.session.commit()

    def add_muted(self, id: int, guild_id: int, user: int) -> None:
        channel = self.get_voice_channel_settings(id, guild_id)
        channel.muted.append(user)
        self.session.commit()

    def remove_muted(self, id: int, guild_id: int, user: int) -> None:
        channel = self.get_voice_channel_settings(id, guild_id)
        channel.muted.remove(user)
        self.session.commit()

    def add_opened(self, id: int, guild_id: int, user: int) -> None:
        channel = self.get_voice_channel_settings(id, guild_id)
        channel.opened.append(user)
        self.session.commit()

    def remove_opened(self, id: int, guild_id: int, user: int) -> None:
        channel = self.get_voice_channel_settings(id, guild_id)
        channel.opened.remove(user)
        self.session.commit()

    # voice channels

    def get_voice_channel(self, id: int, guild_id: int) -> VoiceChannels:
        return self.session.query(VoiceChannels).get([id, guild_id])

    def delete_voice_channel(self, id: int, guild_id: int) -> None:
        return (
            self.session.query(VoiceChannels)
            .filter(VoiceChannels.id == id and VoiceChannels.guild_id == guild_id)
            .delete()
        )

    def add_voice_channel(
        self, id: int, guild_id: int, text_id: int, owner_id: int, message_id: int
    ):
        self.session.add(
            VoiceChannels(
                id=id,
                guild_id=guild_id,
                text_id=text_id,
                owner_id=owner_id,
                message_id=message_id,
            )
        )
        self.session.commit()

    # genshin

    def get_genshin_players(self, guild_id: int) -> list[GenshinProfiles]:
        return self.session.query(GenshinProfiles).filter(
            GenshinProfiles.guild_id == guild_id
        )

    def get_genshin_profile(self, id: int, guild_id: int) -> GenshinProfiles:
        return self.session.query(GenshinProfiles).get([id, guild_id])

    def add_genshin_profile(
        self, id: int, guild_id: int, hoyolab_id: int, genshin_id: int
    ) -> None:
        self.session.add(
            GenshinProfiles(
                id=id, guild_id=guild_id, hoyolab_id=hoyolab_id, genshin_id=genshin_id
            )
        )
        self.session.commit()

    # shikimori

    def get_shikimori_profiles(self, guild_id: int) -> list[ShikimoriProfiles]:
        return self.session.query(ShikimoriProfiles).filter(
            ShikimoriProfiles.guild_id == guild_id
        )

    def add_shikimori_profile(self, id: int, guild_id: int, shikimori_id: int) -> None:
        self.session.add(
            ShikimoriProfiles(id=id, guild_id=guild_id, shikimori_id=shikimori_id)
        )
        self.session.commit()
