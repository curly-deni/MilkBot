from datetime import datetime
from .table_classes import TextMutes, VoiceMutes


class MutesDbMethods:

    # text mutes

    def get_expired_text_mutes(self, guild_id: int) -> list[TextMutes]:
        return self.session.query(TextMutes).filter(
            TextMutes.stop <= datetime.now() and TextMutes.guild_id == guild_id
        )

    def del_text_mute(self, id: int, guild_id: int) -> None:
        mute = self.session.query(TextMutes).filter(
            TextMutes.id == id and TextMutes.guild_id == guild_id
        )
        if mute is not None:
            mute.delete()
            self.session.commit()

    def add_text_mute(self, id: int, guild_id: int, time: datetime) -> None:
        mute = self.session.query(TextMutes).get([id, guild_id])
        if mute is None:
            self.session.add(TextMutes(id=id, guild_id=guild_id, stop=time))
            self.session.commit()

    # voice mutes

    def get_expired_voice_mutes(self, guild_id: int) -> list[VoiceMutes]:
        return self.session.query(VoiceMutes).filter(
            VoiceMutes.stop <= datetime.now() and VoiceMutes.guild_id == guild_id
        )

    def del_voice_mute(self, id: int, guild_id: int) -> None:
        mute = self.session.query(VoiceMutes).filter(
            VoiceMutes.id == id and VoiceMutes.guild_id == guild_id
        )
        if mute is not None:
            mute.delete()
            self.session.commit()

    def add_voice_mute(self, id: int, guild_id: int, time: datetime) -> None:
        mute = self.session.query(VoiceMutes).get[id, guild_id]
        if mute is None:
            self.session.add(VoiceMutes(id=id, guild_id=guild_id, stop=time))
            self.session.commit()
