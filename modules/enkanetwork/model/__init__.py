from typing import List

from pydantic import BaseModel, Field

from .character import CharacterInfo
from .players import PlayerInfo


class EnkaNetworkResponse(BaseModel):
    player: PlayerInfo = Field(None, alias="playerInfo")
    characters: List[CharacterInfo] = Field(None, alias="avatarInfoList")
    ttl: int = 0
