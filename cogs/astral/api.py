from random import randint
import nextcord

from modules.process_runner import AstralScriptRunner as AsyncScript
from modules.async_tables import AsyncTables
from modules.tables import Tables
from datetime import datetime
import asyncio
import os
import sys
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
        self.tables_api = AsyncTables()

        self.status_message: Optional[nextcord.Message] = None

        db_response = self.bot.database.get_astral(channel.guild.id)

        self.script = AsyncScript(sys.executable, os.getcwd(), db_response["script"])

        self.game_spells: Optional[dict] = None
        self.view = None

        try:
            # game param
            self.arena: str = str(
                (response["arena"] if response["arena"] != "R" else str(randint(1, 10)))
            )
        except:
            self.arena = "0"

        if "players" in response:
            self.players_count: int = response["players"]
        else:
            self.players_count: int = 2

        if "dm" in response:
            self.dm: str = response["dm"]
        else:
            self.dm: str = "FALSE"

        if "boss" in response:
            self.boss: Optional[str] = response["boss"]
        else:
            self.boss: Optional[str] = None

        self.players: list[AstralGamePlayer] = []
        self.teams: list[list] = []

    @staticmethod
    async def create(bot, channel: nextcord.TextChannel, response: dict, uuid: str):
        self = AstralGameSession(bot, channel, response, uuid)
        tables = Tables()
        await self.tables_api.autorize()
        self.spread_sheet = tables.create_temp_astral_table(
            self.uuid, self.bot.database.get_tables()["astral"]
        )

        self.spread_sheet_url = (
            "https://docs.google.com/spreadsheets/d/"
            + self.spread_sheet.id
            + "/edit#gid=698078709"
        )
        self.spread_sheet_id = self.spread_sheet.id
        self.bot.logger.debug(f"SpreadSheet URL {self.spread_sheet_url}")

        await self.script.visit(self.spread_sheet_url)

        script_id = await self.tables_api.get_astral_script_id(self.spread_sheet_id)
        self.bot.logger.debug(f"Script ID: {script_id}")

        self.script.script_id = (await self.script.deploy(script_id))[0]
        self.bot.logger.debug(f"Script Answer: {self.script.script_id}")
        self.script.script_id = (self.script.script_id.decode("utf-8"))[:-1]
        self.bot.logger.debug(f"Deployment ID: {self.script.script_id}")

        await self.script.set_gcp(
            script_id, bot.settings["gcp"], bot.settings["profile_path"]
        )
        return self

    def append_player(self, member):
        for player in self.players:
            if player.member == member:
                return
        self.players.append(AstralGamePlayer(member, self))

    def ready_to_start(self):
        if self.bot is None:
            return len(self.players) == self.players_count
        else:
            return len(self.players) == (self.players_count - 1)

    async def start(self):
        # self.bot.logger.info("Run runner process")
        # self.bot.logger.info(await self.script.run())
        if self.status_message is not None:
            await self.status_message.edit(content="Получаю список заклинаний")
        self.game_spells = await self.tables_api.get_game_spells(self.spread_sheet_id)
        if self.game_spells is None or self.game_spells == {}:
            raise GameSpellNotFound

        await self.script.end_game()
        if self.status_message is not None:
            await self.status_message.edit(content="Подготовливаю таблицу")

        if self.players_count == 2:
            self.teams.append([self.players[0]])
        if self.players_count == 4 and self.boss is None and self.dm == "FALSE":
            self.teams.append([self.players[0], self.players[1]])
            self.teams.append([self.players[2], self.players[3]])
        if self.players_count == 4 and self.boss is None and self.dm == "TRUE":
            for player in self.players:
                self.teams.append([player])
        if self.players_count != 2 and self.boss is not None:
            self.teams.append([*self.players])

        if self.boss is not None:
            boss = AstralGamePlayer(self.boss, self)
            self.players.append(boss)
            self.teams.append([boss])
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
        await self.tables_api.set_players_name(self.spread_sheet_id, self.players)
        await self.tables_api.set_arena(self.spread_sheet_id, str(self.arena))
        await self.tables_api.set_dm(self.spread_sheet_id, self.dm)

        if self.players_count > 2 and self.boss is not None:
            await self.tables_api.set_players_teams(
                self.spread_sheet_id, self.players_count
            )

        if self.status_message is not None:
            await self.status_message.edit(content="Стартую игру")
        return await self.script.start_game()

    async def stop(self):
        response = await self.script.end_game()
        # await self.script.destroy()
        return response

    async def put_links(self, c: int) -> bool:
        if c != 4:
            links_array = await self.tables_api.get_players_spreadsheets_links(
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

    async def update_info(self):
        for player in self.players:
            await player.update_info(self.spread_sheet_id, self.tables_api)

    async def get_game_message(self):
        return await self.tables_api.get_game_message(
            self.spread_sheet_id, datetime.now()
        )

    async def try_to_move(self):
        await self.tables_api.set_players_move(self.spread_sheet_id, self.players)
        return await self.script.next_round()

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

    async def update_info(self, spread_sheet_id: str, tables_api):
        if self.member is not None:
            try:
                self.spells: list = await tables_api.get_player_spells(
                    spread_sheet_id, self.name
                )
            except:
                self.spells: list = []
            self.effects: str = await tables_api.get_player_effects(
                spread_sheet_id, self.name
            )
            self.mp = await tables_api.get_player_mp(spread_sheet_id, self.name)

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
