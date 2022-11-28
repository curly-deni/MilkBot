from typing import NoReturn, Optional

from .table_classes import Embeds


class EmbedsDbMethods:
    def get_embed_info(self, message_id: int, channel_id: int) -> Optional[Embeds]:
        return self.session.query(Embeds).get([message_id, channel_id])

    def add_embed_info(
        self, message_id: int, channel_id: int, author_id: int
    ) -> NoReturn:
        profile = self.get_embed_info(message_id, channel_id)
        if profile is None:
            self.session.add(
                Embeds(
                    message_id=message_id, channel_id=channel_id, author_id=author_id
                )
            )
        else:
            profile.author_id = author_id
        self.session.commit()
