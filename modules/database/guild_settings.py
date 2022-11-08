from .table_classes import GuildsSetiings
from typing import Optional


class GuildSettingsDbMethods:

    # guild settings
    def get_guild_info(self, guild_id: int) -> GuildsSetiings:
        guild = self.session.query(GuildsSetiings).get(guild_id)
        if guild is None:
            self.__add_guild_info(guild_id)
            guild = self.session.query(GuildsSetiings).get(guild_id)
        return guild

    def __add_guild_info(self, guild_id: int) -> None:
        guild = self.session.query(GuildsSetiings).get(guild_id)
        if guild is None:
            self.session.add(
                GuildsSetiings(
                    id=guild_id,
                    prefix=self.get_bot_prefix(),
                    admin_roles=[],
                    moderator_roles=[],
                    editor_roles=[],
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
            self.session.commit()

    def get_astral(self, guild_id: int) -> dict:
        guild = self.get_guild_info(guild_id)
        return {"table": guild.astral_table, "script": guild.astral_script}

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
        editor_roles: Optional[list[int]] = None,
        moderator_roles: Optional[list[int]] = None,
        admin_roles: Optional[list[int]] = None,
    ) -> None:
        guild = self.get_guild_info(guild_id)

        if editor_roles is not None:
            guild.editor_roles += editor_roles
        if moderator_roles is not None:
            guild.moderator_roles += moderator_roles
        if admin_roles is not None:
            guild.admin_roles += admin_roles

        self.session.commit()

    def remove_stuff_roles(
        self,
        guild_id: int,
        editor_roles: Optional[list[int]] = None,
        moderator_roles: Optional[list[int]] = None,
        admin_roles: Optional[list[int]] = None,
    ) -> None:
        guild = self.get_guild_info(guild_id)

        if editor_roles is not None:
            for role in editor_roles:
                guild.editor_roles.remove(role)

        if moderator_roles is not None:
            for role in moderator_roles:
                guild.moderator_roles.remove(role)

        if admin_roles is not None:
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
        roles: Optional[list[int]] = None,
        channels: Optional[list[int]] = None,
    ) -> None:
        guild = self.get_guild_info(guild_id)
        guild.horo = status

        if roles is not None and roles:
            guild.horo_roles = roles

        if channels is not None and channels:
            guild.horo_channels = channels

        self.session.commit()

    def set_shikimori_news(
        self,
        guild_id: int,
        status: bool,
        roles: Optional[list[int]] = None,
        channels: Optional[list[int]] = None,
    ) -> None:
        guild = self.get_guild_info(guild_id)
        guild.shikimori_news = status

        if roles is not None and roles:
            guild.shikimori_news_roles = roles

        if channels is not None and channels:
            guild.shikimori_news_channels = channels

        self.session.commit()

    def set_shikimori_releases(
        self,
        guild_id: int,
        status: bool,
        roles: Optional[list[int]] = None,
        channels: Optional[list[int]] = None,
    ) -> None:
        guild = self.get_guild_info(guild_id)
        guild.shikimori_releases = status

        if roles is not None and roles:
            guild.shikimori_releases_roles = roles

        if channels is not None and channels:
            guild.shikimori_releases_channels = channels

        self.session.commit()

    def get_all_horo(self) -> list:
        returnable_list = []
        for guild in self.session.query(GuildsSetiings).all():
            for channel in guild.horo_channels:
                returnable_list.append([channel, guild.horo_roles])
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
