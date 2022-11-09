from .table_classes import ReactionRoles
from typing import Optional, NoReturn


class ReactionRolesDbMethods:
    def get_reaction_roles_info(
        self, message_id: int, channel_id: int
    ) -> Optional[ReactionRoles]:
        return self.session.query(ReactionRoles).get([message_id, channel_id])

    def add_reaction_roles_info(
        self,
        message_id: int,
        channel_id: int,
        author_id: int,
        roles: dict,
        unique: bool,
        single_use: bool,
    ) -> NoReturn:
        profile = self.get_reaction_roles_info(message_id, channel_id)
        prepared_roles = [
            f"{emoji_id}#{role_id}" for emoji_id, role_id in roles.items()
        ]
        if profile is None:
            self.session.add(
                ReactionRoles(
                    message_id=message_id,
                    channel_id=channel_id,
                    author_id=author_id,
                    roles=prepared_roles,
                    unique=unique,
                    single_use=single_use,
                )
            )
        else:
            profile.roles = prepared_roles
            profile.unique = unique
            profile.single_use = single_use
        self.session.commit()

    def delete_reaction_roles_info(self, message_id: int, channel_id: int) -> NoReturn:
        info = self.get_reaction_roles_info(message_id, channel_id)
        if info is not None:
            self.session.query(ReactionRoles).filter(
                ReactionRoles.message_id == message_id,
                ReactionRoles.channel_id == channel_id,
            ).delete()
            self.session.commit()
