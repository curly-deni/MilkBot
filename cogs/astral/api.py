from random import randint
import nextcord
import database.astral as AstralSheetApi
import cogs.astral.scripts as ScriptApi
from datetime import datetime
import asyncio

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
    def __init__(self, bot, channel, response, spreadsheet, script):
        # discord
        self.bot = bot
        self.channel = channel

        self.SheetService = AstralSheetApi.gcAuthorize()
        self.ScriptService = ScriptApi.connectToScriptsApi()
        self.script = script

        # game param
        self.arena = (
            response["arena"] if response["arena"] != "R" else str(randint(1, 10))
        )
        try:
            self.players_count = response["players"]
        except:
            self.players_count = 2

        try:
            self.dm = response["dm"]
        except:
            self.dm = False

        try:
            self.boss = response["boss"]
        except:
            self.boss = None

        self.spreadsheet = spreadsheet

        self.players = []

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

        self.players_ids = []
        for player in self.players:
            if player.member is not None:
                self.players_ids.append(player.member.id)

        AstralSheetApi.inputCastersName(
            self.players, self.spreadsheet, self.SheetService
        )

        AstralSheetApi.setArena(self.arena, self.spreadsheet, self.SheetService)
        AstralSheetApi.setDM(self.dm, self.spreadsheet, self.SheetService)

        ScriptApi.startGame(self.ScriptService, self.script)

    def stop(self):
        ScriptApi.endGame(self.ScriptService, self.script)

    async def putLinks(self, c):
        if c != 4:
            links_array = AstralSheetApi.getCastersSpreadsheetsLinks(
                self.spreadsheet, self.SheetService
            )
            if links_array is None:
                await asyncio.sleep(3)
                await self.putLinks(c + 1)
            else:
                for i in range(len(links_array)):
                    self.players[i].link = links_array[i]
                return True
        else:
            return False

    def updateInfo(self):
        for player in self.players:
            player.updateInfo(self.SheetService, self.spreadsheet)

    async def getGameMessage(self, count):
        if count != 15:
            message = AstralSheetApi.getGameStepMessange(
                self.spreadsheet, self.SheetService, datetime.now()
            )
            try:
                if not message:
                    await self.channel.send("Повторная попытка просчёта хода.")
                    self.move()
                    return await self.getGameMessage(count + 1)
                else:
                    return message
            except:
                return message
        else:
            return False

    def move(self):
        AstralSheetApi.sendCastersMove(
            self.SheetService, self.spreadsheet, self.players
        )
        ScriptApi.nextRound(self.ScriptService, self.script)
        for player in self.players:
            player.newRound()

    def withBot(self):
        for player in self.players:
            if player.member is None:
                return True
        return False


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
        self.movedirection = None

    def newRound(self):
        if self.member is not None:
            self.spells = None
            self.mp = None
            self.effects = None
            self.ability = True
            self.moved = False
            self.move = None
            self.movedirection = None

    def updateInfo(self, SpreadSheetService, SpreadSheet):
        global spells

        if self.member is not None:
            self.spells: list = AstralSheetApi.getCastersMove(
                SpreadSheetService, SpreadSheet, self.name
            )
            self.effects = AstralSheetApi.getEffects(
                SpreadSheet, SpreadSheetService, self.name
            ).lower()
            self.mp = AstralSheetApi.getCastersMP(
                SpreadSheet, SpreadSheetService, self.name
            )

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
