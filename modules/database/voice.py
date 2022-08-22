from .table_classes import VoiceChannels, VoiceChannelsSettings


class VoiceDbMethods:

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
        channel = self.session.query(VoiceChannelsSettings).get([id, guild_id])
        if channel is None:
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
            self.session.commit()

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

    def get_voice_channel_by_text_id(self, id: int, guild_id: int) -> VoiceChannels:
        return self.session.query(VoiceChannels).filter(
            VoiceChannels.guild_id == guild_id and VoiceChannels.text_id == id
        )

    def delete_voice_channel(self, id: int, guild_id: int) -> None:
        channel = self.get_voice_channel(id, guild_id)
        if channel is not None:
            self.session.query(VoiceChannels).filter(
                VoiceChannels.id == id and VoiceChannels.guild_id == guild_id
            ).delete()
            self.session.commit()

    def add_voice_channel(
        self, id: int, guild_id: int, text_id: int, owner_id: int, message_id: int
    ):
        channel = self.get_voice_channel(id, guild_id)
        if channel is None:
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
