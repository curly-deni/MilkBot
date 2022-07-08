from random import randint
import nextcord
import modules.g_app as script_api
import modules.set_gcp as gcp_set_subsystem
import modules.tables
from datetime import datetime
import asyncio
from typing import Optional
from pygsheets import Spreadsheet

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
    def __init__(self, bot, channel, response, uuid):
        self.bot = bot
        self.channel: nextcord.TextChannel = channel
        self.uuid: str = uuid

        self.gcp_subsystem = gcp_set_subsystem.BrowserControl(self.bot)
        self.script = script_api.AstralSheetScriptApi()

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

        try:
            self.boss: Optional[str] = response["boss"]
        except:
            self.boss: Optional[str] = None

        self.players: list[AstralGamePlayer] = []

        self.spread_sheet: Optional[Spreadsheet] = None
        self.spread_sheet_url: Optional[str] = None
        self.spread_sheet_id: Optional[str] = None

    @staticmethod
    async def create(bot, channel, response, uuid):

        self = AstralGameSession(bot, channel, response, uuid)

        self.spread_sheet = self.bot.tables.create_temp_astral_table(self.uuid)

        self.spread_sheet_url = self.spread_sheet.url + "/edit#gid=698078709"
        self.spread_sheet_id = self.spread_sheet.id
        self.bot.logger.debug(f"SpreadSheet URL {self.spread_sheet_url}")

        self.gcp_subsystem.browser.get(self.spread_sheet_url)

        await asyncio.sleep(10)

        script_id = self.bot.tables.get_astral_script_id(self.spread_sheet_url)
        self.bot.logger.debug(f"Script ID: {script_id}")

        self.script.script_id = self.script.deploy(script_id)["deploymentId"]
        self.bot.logger.debug(f"Deployment ID: {self.script.script_id}")

        self.gcp_subsystem.set_gcp(script_id)
        self.gcp_subsystem.browser.close()

        return self

    def append_player(self, member):
        for player in self.players:
            if player.member == member:
                return
        self.players.append(AstralGamePlayer(member))

    def ready_to_start(self):
        return len(self.players) == self.players_count

    def start(self):
        if self.boss is not None:
            self.players.append(AstralGamePlayer(self.boss))

        self.players_ids = [
            player.member.id for player in self.players if player.member is not None
        ]

        self.bot.tables.set_players_name(self.spread_sheet_id, self.players)
        self.bot.tables.set_arena(self.spread_sheet_id, self.arena)
        self.bot.tables.set_dm(self.spread_sheet_id, self.dm)

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
    def __init__(self, member):
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

        self.link = None

        self.spells = None
        self.mp = None
        self.effects = None

        self.move = None
        self.move_direction = None

    def new_round(self):
        if self.member is not None:
            self.spells = None
            self.mp = None
            self.effects = None
            self.ability = True
            self.moved = False
            self.move = None
            self.move_direction = None

    def round_replay(self):
        if self.member is not None:
            self.moved = False
            self.move = None
            self.move_direction = None

    def update_info(self, spread_sheet_id: str, tables_api: modules.tables.Tables):
        global spells

        if self.member is not None:
            self.spells: list = tables_api.get_player_spells(spread_sheet_id, self.name)
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
