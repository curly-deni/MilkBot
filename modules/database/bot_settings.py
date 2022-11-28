from datetime import datetime

from .table_classes import BotSettings


class BotSettingsDbMethods:

    # bot settings
    def get_bot_settings(self) -> BotSettings:
        return self.session.query(BotSettings).get(0)

    def get_bot_prefix(self) -> str:
        return self.get_bot_settings().base_prefix

    def get_tables(self) -> dict:
        bot_settings = self.get_bot_settings()
        return {
            "astral": bot_settings.base_astral_table,
            "embeds": bot_settings.base_embeds_table,
            "art": bot_settings.base_art_table,
        }

    def get_last_news_time(self) -> datetime:
        return self.get_bot_settings().shikimori_last_news_time

    def set_last_news_time(self, time: datetime) -> None:
        bot_settings = self.get_bot_settings()
        bot_settings.shikimori_last_news_time = time
        self.session.commit()
