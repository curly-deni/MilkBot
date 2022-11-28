from random import choice
from typing import NoReturn, Optional

from .table_classes import RPCustomGif


class RPCustomGifDbMethods:
    def get_guild_rp_custom_gif(self, guild_id: int) -> RPCustomGif:
        gif_list = self.session.query(RPCustomGif).get(guild_id)
        if gif_list is None:
            self.__add_guild_rp_custom_gif(guild_id)
            return self.get_guild_rp_custom_gif(guild_id)
        return gif_list

    def __add_guild_rp_custom_gif(self, guild_id: int) -> NoReturn:
        self.session.add(
            RPCustomGif(
                guild_id=guild_id,
                hug=[],
                smile=[],
                poke=[],
                slap=[],
                bite=[],
                cry=[],
                blush=[],
                kiss=[],
                lick=[],
                pat=[],
                feed=[],
            )
        )
        self.session.commit()

    def get_hug_gif(self, guild_id: int) -> Optional[str]:
        gif_list = self.get_guild_rp_custom_gif(guild_id)
        if not gif_list.hug:
            return None

        return choice(gif_list.hug)

    def get_all_hug_gif(self, guild_id) -> list:
        return self.get_guild_rp_custom_gif(guild_id).hug

    def add_hug_gif(self, guild_id: int, url: str) -> NoReturn:
        gif_list = self.get_guild_rp_custom_gif(guild_id)
        gif_list.hug.append(url)
        self.session.commit()

    def set_hug_gifs(self, guild_id: int, urls: list[str]) -> NoReturn:
        gif_list = self.get_guild_rp_custom_gif(guild_id)
        gif_list.hug = urls
        self.session.commit()

    def get_smile_gif(self, guild_id: int) -> Optional[str]:
        gif_list = self.get_guild_rp_custom_gif(guild_id)
        if not gif_list.smile:
            return None

        return choice(gif_list.smile)

    def get_all_smile_gif(self, guild_id) -> list:
        return self.get_guild_rp_custom_gif(guild_id).smile

    def add_smile_gif(self, guild_id: int, url: str) -> NoReturn:
        gif_list = self.get_guild_rp_custom_gif(guild_id)
        gif_list.smile.append(url)
        self.session.commit()

    def set_smile_gifs(self, guild_id: int, urls: list[str]) -> NoReturn:
        gif_list = self.get_guild_rp_custom_gif(guild_id)
        gif_list.smile = urls
        self.session.commit()

    def get_poke_gif(self, guild_id: int) -> Optional[str]:
        gif_list = self.get_guild_rp_custom_gif(guild_id)
        if not gif_list.poke:
            return None

        return choice(gif_list.poke)

    def get_all_poke_gif(self, guild_id) -> list:
        return self.get_guild_rp_custom_gif(guild_id).poke

    def add_poke_gif(self, guild_id: int, url: str) -> NoReturn:
        gif_list = self.get_guild_rp_custom_gif(guild_id)
        gif_list.poke.append(url)
        self.session.commit()

    def set_poke_gifs(self, guild_id: int, urls: list[str]) -> NoReturn:
        gif_list = self.get_guild_rp_custom_gif(guild_id)
        gif_list.poke = urls
        self.session.commit()

    def get_slap_gif(self, guild_id: int) -> Optional[str]:
        gif_list = self.get_guild_rp_custom_gif(guild_id)
        if not gif_list.slap:
            return None

        return choice(gif_list.slap)

    def get_all_slap_gif(self, guild_id) -> list:
        return self.get_guild_rp_custom_gif(guild_id).slap

    def add_slap_gif(self, guild_id: int, url: str) -> NoReturn:
        gif_list = self.get_guild_rp_custom_gif(guild_id)
        gif_list.slap.append(url)
        self.session.commit()

    def set_slap_gifs(self, guild_id: int, urls: list[str]) -> NoReturn:
        gif_list = self.get_guild_rp_custom_gif(guild_id)
        gif_list.slap = urls
        self.session.commit()

    def get_bite_gif(self, guild_id: int) -> Optional[str]:
        gif_list = self.get_guild_rp_custom_gif(guild_id)
        if not gif_list.bite:
            return None

        return choice(gif_list.bite)

    def get_all_bite_gif(self, guild_id) -> list:
        return self.get_guild_rp_custom_gif(guild_id).bite

    def add_bite_gif(self, guild_id: int, url: str) -> NoReturn:
        gif_list = self.get_guild_rp_custom_gif(guild_id)
        gif_list.bite.append(url)
        self.session.commit()

    def set_bite_gifs(self, guild_id: int, urls: list[str]) -> NoReturn:
        gif_list = self.get_guild_rp_custom_gif(guild_id)
        gif_list.bite = urls
        self.session.commit()

    def get_cry_gif(self, guild_id: int) -> Optional[str]:
        gif_list = self.get_guild_rp_custom_gif(guild_id)
        if not gif_list.cry:
            return None

        return choice(gif_list.cry)

    def get_all_cry_gif(self, guild_id) -> list:
        return self.get_guild_rp_custom_gif(guild_id).cry

    def add_cry_gif(self, guild_id: int, url: str) -> NoReturn:
        gif_list = self.get_guild_rp_custom_gif(guild_id)
        gif_list.cry.append(url)
        self.session.commit()

    def set_cry_gifs(self, guild_id: int, urls: list[str]) -> NoReturn:
        gif_list = self.get_guild_rp_custom_gif(guild_id)
        gif_list.cry = urls
        self.session.commit()

    def get_blush_gif(self, guild_id: int) -> Optional[str]:
        gif_list = self.get_guild_rp_custom_gif(guild_id)
        if not gif_list.blush:
            return None

        return choice(gif_list.blush)

    def get_all_blush_gif(self, guild_id) -> list:
        return self.get_guild_rp_custom_gif(guild_id).blush

    def add_blush_gif(self, guild_id: int, url: str) -> NoReturn:
        gif_list = self.get_guild_rp_custom_gif(guild_id)
        gif_list.blush.append(url)
        self.session.commit()

    def set_blush_gifs(self, guild_id: int, urls: list[str]) -> NoReturn:
        gif_list = self.get_guild_rp_custom_gif(guild_id)
        gif_list.blush = urls
        self.session.commit()

    def get_kiss_gif(self, guild_id: int) -> Optional[str]:
        gif_list = self.get_guild_rp_custom_gif(guild_id)
        if not gif_list.kiss:
            return None

        return choice(gif_list.kiss)

    def get_all_kiss_gif(self, guild_id) -> list:
        return self.get_guild_rp_custom_gif(guild_id).kiss

    def add_kiss_gif(self, guild_id: int, url: str) -> NoReturn:
        gif_list = self.get_guild_rp_custom_gif(guild_id)
        gif_list.kiss.append(url)
        self.session.commit()

    def set_kiss_gifs(self, guild_id: int, urls: list[str]) -> NoReturn:
        gif_list = self.get_guild_rp_custom_gif(guild_id)
        gif_list.kiss = urls
        self.session.commit()

    def get_lick_gif(self, guild_id: int) -> Optional[str]:
        gif_list = self.get_guild_rp_custom_gif(guild_id)
        if not gif_list.lick:
            return None

        return choice(gif_list.lick)

    def get_all_lick_gif(self, guild_id) -> list:
        return self.get_guild_rp_custom_gif(guild_id).lick

    def add_lick_gif(self, guild_id: int, url: str) -> NoReturn:
        gif_list = self.get_guild_rp_custom_gif(guild_id)
        gif_list.lick.append(url)
        self.session.commit()

    def set_lick_gifs(self, guild_id: int, urls: list[str]) -> NoReturn:
        gif_list = self.get_guild_rp_custom_gif(guild_id)
        gif_list.lick = urls
        self.session.commit()

    def get_pat_gif(self, guild_id: int) -> Optional[str]:
        gif_list = self.get_guild_rp_custom_gif(guild_id)
        if not gif_list.pat:
            return None

        return choice(gif_list.pat)

    def get_all_pat_gif(self, guild_id) -> list:
        return self.get_guild_rp_custom_gif(guild_id).pat

    def add_pat_gif(self, guild_id: int, url: str) -> NoReturn:
        gif_list = self.get_guild_rp_custom_gif(guild_id)
        gif_list.pat.append(url)
        self.session.commit()

    def set_pat_gifs(self, guild_id: int, urls: list[str]) -> NoReturn:
        gif_list = self.get_guild_rp_custom_gif(guild_id)
        gif_list.pat = urls
        self.session.commit()

    def get_feed_gif(self, guild_id: int) -> Optional[str]:
        gif_list = self.get_guild_rp_custom_gif(guild_id)
        if not gif_list.feed:
            return None

        return choice(gif_list.feed)

    def get_all_feed_gif(self, guild_id) -> list:
        return self.get_guild_rp_custom_gif(guild_id).feed

    def add_feed_gif(self, guild_id: int, url: str) -> NoReturn:
        gif_list = self.get_guild_rp_custom_gif(guild_id)
        gif_list.feed.append(url)
        self.session.commit()

    def set_feed_gifs(self, guild_id: int, urls: list[str]) -> NoReturn:
        gif_list = self.get_guild_rp_custom_gif(guild_id)
        gif_list.feed = urls
        self.session.commit()
