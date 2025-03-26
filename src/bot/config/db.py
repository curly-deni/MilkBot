from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ["DB_SETTINGS", "DB_PROTOCOL", "DB_LIB_SCHEMA", "DB_APP_SCHEMA"]

DB_PROTOCOL = "postgresql+asyncpg"

DB_LIB_SCHEMA = "modules"
DB_APP_SCHEMA = "public"


class Settings(BaseSettings):
    BOT_USER: str
    BOT_PASSWORD: str
    HOST: str
    PORT: int

    model_config = SettingsConfigDict(env_prefix="DB_")

    def get_url(self):
        return (
            f"{DB_PROTOCOL}://{self.BOT_USER}:{self.BOT_PASSWORD}@"
            f"{self.HOST}:{self.PORT}/{self.BOT_USER}"
        )


DB_SETTINGS = Settings()
