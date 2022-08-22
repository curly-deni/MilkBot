from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, BigInteger, TIMESTAMP, Boolean, ARRAY
from sqlalchemy.ext.mutable import MutableList

Base = declarative_base()


class BotSettings(Base):
    __tablename__ = "bot_settings"

    id = Column(Integer, primary_key=True)
    base_prefix = Column(String)
    base_astral_table = Column(String)
    base_embeds_table = Column(String)
    base_art_table = Column(String)
    shikimori_last_news_time = Column(TIMESTAMP)


class Embeds(Base):
    __tablename__ = "embeds"

    id = Column(BigInteger, primary_key=True)
    guild_id = Column(BigInteger, primary_key=True)
    channel_id = Column(BigInteger)
    json = Column(String)


class GuildsSetiings(Base):
    __tablename__ = "guilds_settings"

    id = Column(BigInteger, primary_key=True)

    admin_roles = Column(MutableList.as_mutable(ARRAY(BigInteger)))
    moderator_roles = Column(MutableList.as_mutable(ARRAY(BigInteger)))
    editor_roles = Column(MutableList.as_mutable(ARRAY(BigInteger)))

    prefix = Column(String)
    embeds_table = Column(String)
    astral_table = Column(String)
    art_table = Column(String)
    astral_script = Column(String)
    disabled_functions = Column(MutableList.as_mutable(ARRAY(String)))

    # anime horoscope
    horo = Column(Boolean)
    horo_roles = Column(MutableList.as_mutable(ARRAY(BigInteger)))
    horo_channels = Column(MutableList.as_mutable(ARRAY(BigInteger)))

    # neural horoscope
    neuralhoro = Column(Boolean)
    neuralhoro_roles = Column(MutableList.as_mutable(ARRAY(BigInteger)))
    neuralhoro_channels = Column(MutableList.as_mutable(ARRAY(BigInteger)))

    shikimori_news = Column(Boolean)
    shikimori_news_roles = Column(MutableList.as_mutable(ARRAY(BigInteger)))
    shikimori_news_channels = Column(MutableList.as_mutable(ARRAY(BigInteger)))

    shikimori_releases = Column(Boolean)
    shikimori_releases_roles = Column(MutableList.as_mutable(ARRAY(BigInteger)))
    shikimori_releases_channels = Column(MutableList.as_mutable(ARRAY(BigInteger)))

    voice_channel_generator = Column(BigInteger)
    voice_channel_category = Column(BigInteger)


class GenshinProfiles(Base):
    __tablename__ = "genshin_profiles"

    id = Column(BigInteger, primary_key=True)
    guild_id = Column(BigInteger, primary_key=True)

    genshin_id = Column(Integer)

    cookies_ltuid = Column(String)
    cookies_lttoken = Column(String)


class GuildsStatistics(Base):
    __tablename__ = "guilds_statistics"

    id = Column(BigInteger, primary_key=True)
    guild_id = Column(BigInteger, primary_key=True)

    xp = Column(BigInteger)
    lvl = Column(Integer)
    cookies = Column(Integer)
    voice_time = Column(BigInteger)
    citation = Column(String)
    coins = Column(Integer)
    gems = Column(Integer)


class ShikimoriProfiles(Base):
    __tablename__ = "shikimori_profiles"

    id = Column(BigInteger, primary_key=True)
    guild_id = Column(BigInteger, primary_key=True)

    shikimori_id = Column(Integer)


class TextMutes(Base):
    __tablename__ = "text_mutes"

    id = Column(BigInteger, primary_key=True)
    guild_id = Column(BigInteger, primary_key=True)

    reason = Column(String)
    stop = Column(TIMESTAMP)


class VoiceMutes(Base):
    __tablename__ = "voice_mutes"

    id = Column(BigInteger, primary_key=True)
    guild_id = Column(BigInteger, primary_key=True)

    reason = Column(String)
    stop = Column(TIMESTAMP)


class VoiceChannels(Base):
    __tablename__ = "voice_channels"

    id = Column(BigInteger, primary_key=True)
    guild_id = Column(BigInteger, primary_key=True)

    text_id = Column(BigInteger)
    owner_id = Column(BigInteger)
    message_id = Column(BigInteger)


class VoiceChannelsSettings(Base):
    __tablename__ = "voice_channels_settings"

    id = Column(BigInteger, primary_key=True)
    guild_id = Column(BigInteger, primary_key=True)

    name = Column(String)
    bitrate = Column(Integer)
    limit = Column(Integer)
    open = Column(Boolean)

    banned = Column(MutableList.as_mutable(ARRAY(BigInteger)))
    muted = Column(MutableList.as_mutable(ARRAY(BigInteger)))
    opened = Column(MutableList.as_mutable(ARRAY(BigInteger)))
