from datetime import datetime

import inflect
from sqlalchemy import Integer, func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column

from framecho.utils import camel_to_snake

p = inflect.engine()

__all__ = ["Base"]


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    @declared_attr.directive
    def __tablename__(cls) -> str:  # noqa
        # noinspection PyTypeChecker
        return p.plural(camel_to_snake(cls.__name__))
