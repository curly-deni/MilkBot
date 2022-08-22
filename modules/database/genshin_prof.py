from .table_classes import GenshinProfiles


class GenshinProfilesDbMethods:

    # genshin

    def get_genshin_players(self, guild_id: int) -> list[GenshinProfiles]:
        return self.session.query(GenshinProfiles).filter(
            GenshinProfiles.guild_id == guild_id
        )

    def get_genshin_profile(self, id: int, guild_id: int) -> GenshinProfiles:
        return self.session.query(GenshinProfiles).get([id, guild_id])

    def add_genshin_profile(self, id: int, guild_id: int, genshin_id: int) -> None:
        profile = self.get_genshin_profile(id, guild_id)
        if profile is None:
            self.session.add(
                GenshinProfiles(
                    id=id,
                    guild_id=guild_id,
                    genshin_id=genshin_id,
                )
            )
        else:
            profile.genshin_id = genshin_id
        self.session.commit()
