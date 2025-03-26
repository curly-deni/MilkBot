from framecho.db import Base as LBase


class Base(LBase):
    __abstract__ = True

    __table_args__ = {"schema": "app"}
