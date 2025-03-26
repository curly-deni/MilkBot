from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger

from .base import Base


class GuildPrefix(Base):
    guild_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    prefix: Mapped[str] = mapped_column(nullable=True)
