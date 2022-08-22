from .table_classes import ShikimoriProfiles


class ShikimoriProfilesDbMethods:
    def get_shikimori_profile(self, id: int, guild_id: int) -> ShikimoriProfiles:
        return self.session.query(ShikimoriProfiles).get([id, guild_id])

    def get_shikimori_profiles(self, guild_id: int) -> list[ShikimoriProfiles]:
        return self.session.query(ShikimoriProfiles).filter(
            ShikimoriProfiles.guild_id == guild_id
        )

    def add_shikimori_profile(self, id: int, guild_id: int, shikimori_id: int) -> None:
        profile = self.get_shikimori_profile(id, guild_id)
        if profile is None:
            self.session.add(
                ShikimoriProfiles(id=id, guild_id=guild_id, shikimori_id=shikimori_id)
            )
        else:
            profile.shikimori_id = shikimori_id
        self.session.commit()
