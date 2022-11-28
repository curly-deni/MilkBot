from sqlalchemy import desc

from .lvl_count_func import count_new_lvl
from .table_classes import GuildsStatistics


class GuildStatisticDbMethods:
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
        member = self.session.query(GuildsStatistics).get([id, guild_id])
        if member is None:
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
