from random import randint
import nextcord
import modules.g_app as script_api
import modules.tables
from datetime import datetime
import asyncio
from typing import Optional

from .exceptions import GameSpellNotFound

skills = [
    "м",
    "б",
    "д",
    "л",
    "гг",
    "о",
    "ж",
    "ф",
    "п",
    "с",
]


class AstralGameSession(object):
    def __init__(self, bot, channel: nextcord.TextChannel, response: dict, uuid: str):
        self.bot = bot
        self.channel: nextcord.TextChannel = channel
        self.uuid: str = uuid

        self.status_message: Optional[nextcord.Message] = None

        db_response = self.bot.database.get_astral(channel.guild.id)

        self.script = script_api.AstralSheetScriptApi(db_response["script"])
        self.spread_sheet_id: Optional[str] = db_response["table"]

        self.game_spells: Optional[dict] = None
        self.view = None

        try:
            # game param
            self.arena: int = int(
                (response["arena"] if response["arena"] != "R" else str(randint(1, 10)))
            )
        except:
            self.arena = 0

        if "players" in response:
            self.players_count: int = response["players"]
        else:
            self.players_count: int = 2

        if "dm" in response:
            self.dm: bool = response["dm"]
        else:
            self.dm: bool = False

        if "boss" in response:
            self.boss: Optional[str] = response["boss"]
        else:
            self.boss: Optional[str] = None

        self.players: list[AstralGamePlayer] = []

    def append_player(self, member):
        for player in self.players:
            if player.member == member:
                return
        self.players.append(AstralGamePlayer(member, self))

    def ready_to_start(self):
        return len(self.players) == self.players_count

    async def start(self):
        if self.status_message is not None:
            await self.status_message.edit(content="Получаю список заклинаний")
        self.game_spells = self.bot.tables.get_game_spells(self.spread_sheet_id)
        if self.game_spells is None or self.game_spells == {}:
            raise GameSpellNotFound

        self.script.end_game()
        if self.status_message is not None:
            await self.status_message.edit(content="Подготовливаю таблицу")

        if self.boss is not None:
            self.players.append(AstralGamePlayer(self.boss, self))
            if self.status_message is not None:
                await self.status_message.edit(
                    content="Добавляю виртуального противника"
                )

        if self.status_message is not None:
            await self.status_message.edit(content="Генерирую alias-таблицу")
        self.players_ids = [
            player.member.id for player in self.players if player.member is not None
        ]

        if self.status_message is not None:
            await self.status_message.edit(content="Вношу данные об игре в таблицу")
        self.bot.tables.set_players_name(self.spread_sheet_id, self.players)
        self.bot.tables.set_arena(self.spread_sheet_id, self.arena)
        self.bot.tables.set_dm(self.spread_sheet_id, self.dm)

        if self.status_message is not None:
            await self.status_message.edit(content="Стартую игру")
        return self.script.start_game()

    def stop(self):
        return self.script.end_game()

    async def put_links(self, c: int) -> bool:
        if c != 4:
            links_array = self.bot.tables.get_players_spreadsheets_links(
                self.spread_sheet_id
            )
            if links_array is None:
                await asyncio.sleep(3)
                await self.put_links(c + 1)
            else:
                for i in range(len(links_array)):
                    self.players[i].link = links_array[i]
                return True
        else:
            return False

    def update_info(self):
        for player in self.players:
            player.update_info(self.spread_sheet_id, self.bot.tables)

    async def get_game_message(self):
        return self.bot.tables.get_game_message(self.spread_sheet_id, datetime.now())

    def try_to_move(self):
        self.bot.tables.set_players_move(self.spread_sheet_id, self.players)
        return self.script.next_round()

    def prepare_for_new_round(self):
        for player in self.players:
            player.new_round()

    def round_replay(self):
        for player in self.players:
            player.round_replay()

    def with_bot(self):
        return any([player for player in self.players if player.member is None])


class AstralGamePlayer(object):
    def __init__(self, member, game):
        if isinstance(member, nextcord.Member):
            self.member = member
            self.name = member.display_name

            self.ability = True
            self.moved = False

        else:
            self.name = member
            self.member = None
            self.ability = False
            self.moved = False

        self.game = game
        self.link = None

        self.spells = None
        self.mp = None
        self.effects = None

        self.move = None
        self.move_direction = None

    def new_round(self):
        if self.member is not None:
            del self.spells
            del self.mp
            del self.effects
            del self.ability
            del self.moved
            del self.move
            del self.move_direction

            self.spells = None
            self.mp = None
            self.effects = None
            self.ability = True
            self.moved = False
            self.move = None
            self.move_direction = None

    def round_replay(self):
        if self.member is not None:
            del self.moved
            del self.move
            del self.move_direction

            self.moved = False
            self.move = None
            self.move_direction = None

    def update_info(self, spread_sheet_id: str, tables_api: modules.tables.Tables):
        if self.member is not None:
            try:
                self.spells: list = tables_api.get_player_spells(
                    spread_sheet_id, self.name
                )
            except:
                self.spells: list = []
            self.effects: str = tables_api.get_player_effects(
                spread_sheet_id, self.name
            ).lower()
            self.mp = tables_api.get_player_mp(spread_sheet_id, self.name)

            stan = self.effects.find("сон") != -1 or self.effects.find("стан") != -1

            if stan:
                check233 = "233" in self.spells
                check258 = "258" in self.spells
                check = check233 or check258
                self.spells = []
                if not check:
                    self.ability = False
                    self.moved = True
                else:
                    if check233:
                        self.spells.append("233")
                    if check258:
                        self.spells.append("258")
                    self.spells += skills
            else:
                self.spells += skills
