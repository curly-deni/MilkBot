from .table_classes import RolesSaver


class RolesSaverDbMethods:
    def get_user_roles(self, id: int, guild_id: int) -> RolesSaver:
        return self.session.query(RolesSaver).get([id, guild_id])

    def add_user_roles(self, id: int, guild_id: int, roles: list[int]) -> None:
        profile = self.get_user_roles(id, guild_id)
        if profile is None:
            self.session.add(RolesSaver(id=id, guild_id=guild_id, roles=roles))
        else:
            profile.roles = roles
        self.session.commit()
