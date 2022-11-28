from sqlalchemy import ARRAY, TIMESTAMP, BigInteger, Boolean, Column, Integer, String
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class BotSettings(Base):
    __tablename__ = "bot_settings"

    id = Column(Integer, primary_key=True)
    base_prefix = Column(String)
    base_astral_table = Column(String)
    base_embeds_table = Column(String)
    base_art_table = Column(String)
    shikimori_last_news_time = Column(TIMESTAMP)


class GuildsSetiings(Base):
    __tablename__ = "guilds_settings"

    id = Column(BigInteger, primary_key=True)

    admin_roles = Column(MutableList.as_mutable(ARRAY(BigInteger)))
    moderator_roles = Column(MutableList.as_mutable(ARRAY(BigInteger)))
    editor_roles = Column(MutableList.as_mutable(ARRAY(BigInteger)))

    prefix = Column(String)
    astral_table = Column(String)
    astral_script = Column(String)

    # anime horoscope
    horo = Column(Boolean)
    horo_roles = Column(MutableList.as_mutable(ARRAY(BigInteger)))
    horo_channels = Column(MutableList.as_mutable(ARRAY(BigInteger)))

    shikimori_news = Column(Boolean)
    shikimori_news_roles = Column(MutableList.as_mutable(ARRAY(BigInteger)))
    shikimori_news_channels = Column(MutableList.as_mutable(ARRAY(BigInteger)))

    shikimori_releases = Column(Boolean)
    shikimori_releases_roles = Column(MutableList.as_mutable(ARRAY(BigInteger)))
    shikimori_releases_channels = Column(MutableList.as_mutable(ARRAY(BigInteger)))

    voice_channel_generator = Column(BigInteger)
    voice_channel_category = Column(BigInteger)

    need_verify = Column(Boolean)
    restore_roles = Column(Boolean)

    verify_roles = Column(MutableList.as_mutable(ARRAY(BigInteger)))
    verify = Column(Boolean)

    verify_notify = Column(Boolean)
    verify_notify_channel = Column(BigInteger)
    verify_notify_phrases = Column(MutableList.as_mutable(ARRAY(String)))

    verifed_user_leave_notify = Column(Boolean)
    verifed_user_leave_notify_channel = Column(BigInteger)
    verifed_user_leave_notify_phrases = Column(MutableList.as_mutable(ARRAY(String)))


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


class Embeds(Base):
    __tablename__ = "embeds"

    message_id = Column(Integer, primary_key=True)
    channel_id = Column(Integer, primary_key=True)

    author_id = Column(Integer)


class ReactionRoles(Base):
    __tablename__ = "reaction_roles"

    message_id = Column(Integer, primary_key=True)
    channel_id = Column(Integer, primary_key=True)
    author_id = Column(Integer)

    roles = Column(MutableList.as_mutable(ARRAY(String)))
    unique = Column(Boolean)
    single_use = Column(Boolean)
    verify = Column(Boolean)


class RolesSaver(Base):
    __tablename__ = "roles_saver"

    id = Column(BigInteger, primary_key=True)
    guild_id = Column(BigInteger, primary_key=True)
    roles = Column(MutableList.as_mutable(ARRAY(BigInteger)))


class RPCustomGif(Base):
    __tablename__ = "rp_custom_gif"

    guild_id = Column(BigInteger, primary_key=True)

    hug = Column(MutableList.as_mutable(ARRAY(String)))
    smile = Column(MutableList.as_mutable(ARRAY(String)))
    poke = Column(MutableList.as_mutable(ARRAY(String)))
    slap = Column(MutableList.as_mutable(ARRAY(String)))
    bite = Column(MutableList.as_mutable(ARRAY(String)))
    cry = Column(MutableList.as_mutable(ARRAY(String)))
    blush = Column(MutableList.as_mutable(ARRAY(String)))
    kiss = Column(MutableList.as_mutable(ARRAY(String)))
    lick = Column(MutableList.as_mutable(ARRAY(String)))
    pat = Column(MutableList.as_mutable(ARRAY(String)))
    feed = Column(MutableList.as_mutable(ARRAY(String)))
