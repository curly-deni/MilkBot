import pygsheets
from random import choice
from datetime import datetime
from nextcord.ext import tasks
from typing import Union, Optional
import numpy as np


class Tables:
    def __init__(self, bot=None):
        self.table_session = pygsheets.authorize(
            client_secret=r"tokens\client_secret.json",
            credentials_directory=r"tokens",
        )
        self.bot = bot

    @tasks.loop(hours=4)
    async def reconnect(self) -> None:
        self.table_session = pygsheets.authorize()

    # art

    def get_art(self, guild_id: int, title: str) -> Optional[str]:

        table = self.bot.database.get_guild_info(guild_id).art_table
        if table is not None:
            spread_sheet = self.table_session.open_by_key(table)
            sheet = spread_sheet.worksheet_by_title(title)
            list_of_arts = sheet.get_values("A2", "B1001")

            art = choice(list_of_arts)
            art_index = list_of_arts.index(art) + 2

            if art[1] == "":
                art_counter = 0
            else:
                art_counter = int(art[1])
            sheet.update_value(f"B{art_index}", art_counter + 1)

            return art[0]
        else:
            return None

    def create_art_table(self, guild_id: int) -> None:
        spread_sheet = self.table_session.create(
            f"Art-{guild_id}", template=self.bot.database.get_tables()["art"]
        )

        spread_sheet.share("", role="writer", type="anyone")
        sheet = spread_sheet.sheet1
        sheet.update_value("D1", f"{guild_id}")

        guild = self.bot.database.get_guild_info(guild_id)
        guild.art_table = spread_sheet.id
        self.bot.database.session.commit()

    # embeds

    def get_embeds(self, guild_id: int) -> Optional[list[list]]:

        table = self.bot.database.get_guild_info(guild_id).embeds_table
        if table is not None:
            spread_sheet = self.table_session.open_by_key(table)
            sheet = spread_sheet.sheet1
            return sheet.get_values("O2", "V1000")
        else:
            return None

    def update_embed(self, guild_id: int, message_id: int, num: int) -> None:

        table = self.bot.database.get_guild_info(guild_id).embeds_table
        if table is not None:
            spread_sheet = self.table_session.open_by_key(table)
            sheet = spread_sheet.sheet1

            sheet.update_value(f"A{num}", str(message_id))
            sheet.update_value(f"I{num}", False)

    def create_embeds_table(self, guild_id: int) -> None:
        spread_sheet = self.table_session.create(
            f"Emb-{guild_id}", template=self.bot.database.get_tables()["embeds"]
        )

        spread_sheet.share("", role="writer", type="anyone")
        sheet = spread_sheet.sheet1
        sheet.update_value("B1", f"{guild_id}")

        guild = self.bot.database.get_guild_info(guild_id)
        guild.embeds_table = spread_sheet.id
        self.bot.database.session.commit()

    # astral

    def set_players_name(self, spread_sheet_id: str, players: list) -> None:
        spread_sheet = self.table_session.open_by_key(spread_sheet_id)
        sheet = spread_sheet.worksheet_by_title("Настройки")

        for count, value in enumerate(players):
            sheet.update_value(f"A{count + 2}", value.name)

    def get_players_name(self, spread_sheet_id: str) -> list:
        spread_sheet = self.table_session.open_by_key(spread_sheet_id)
        sheet = spread_sheet.worksheet_by_title("Настройки")
        return list(np.array(sheet.get_values("A2", "A6")).ravel())

    def get_players_spreadsheets_links(self, spread_sheet_id: str) -> list:
        spread_sheet_id = self.table_session.open_by_key(spread_sheet_id)
        sheet = spread_sheet_id.worksheet_by_title("Настройки")
        return list(np.array(sheet.get_values("D2", "D6")).ravel())

    def set_players_move(self, spread_sheet_id: str, players: list) -> None:
        spread_sheet_id = self.table_session.open_by_key(spread_sheet_id)
        sheet = spread_sheet_id.worksheet_by_title("Основная")
        for count, value in enumerate(players):
            sheet.update_value(f"C{count + 2}", value.move)
            sheet.update_value(f"D{count + 2}", value.move_direction)

    def get_player_spells(self, spread_sheet_id: str, player: str) -> list:
        spread_sheet_id = self.table_session.open_by_key(spread_sheet_id)
        sheet = spread_sheet_id.worksheet_by_title(player)
        try:
            spells = sheet.get_value("Q90")
            if spells is None or spells == "":
                raise Exception
        except:
            return self.get_player_spells(spread_sheet_id, player)
        return spells.split(", ")

    def get_game_message(
        self, spread_sheet_id: str, time: datetime
    ) -> Union[list, bool]:
        spread_sheet = self.table_session.open_by_key(spread_sheet_id)
        sheet = spread_sheet.worksheet_by_title("Основная")
        try:
            message = sheet.get_value("I6")
            if message is None or message == "":
                raise Exception
        except:
            if (datetime.now() - time).total_seconds() <= 15:
                return self.get_game_message(spread_sheet_id, time)
            else:
                return False
        message_list = ["", []]
        g = message.split("\n")
        l = g[0].split(" ")
        for i in l:
            if i != "":
                message_list[1].append(i)
        for i in range(4):
            g.pop(0)
        message_list[0] = ("\n").join(g)
        return message_list

    def set_arena(self, spread_sheet_id: str, arena: str) -> None:
        spread_sheet = self.table_session.open_by_key(spread_sheet_id)
        sheet = spread_sheet.worksheet_by_title("Настройки")
        sheet.update_value("I3", arena)

    def set_dm(self, spread_sheet_id: str, dm: bool) -> None:
        spread_sheet = self.table_session.open_by_key(spread_sheet_id)
        sheet = spread_sheet.worksheet_by_title("Настройки")
        sheet.update_value("I3", dm)

    def get_player_effects(self, spread_sheet_id: str, player: str) -> str:
        spread_sheet = self.table_session.open_by_key(spread_sheet_id)
        main_sheet = spread_sheet.worksheet_by_title("Основная")
        try:
            game_round = main_sheet.get_value("H2")
            if game_round is None or game_round == "":
                raise Exception
        except:
            return self.get_player_effects(spread_sheet_id, player)

        player_sheet = spread_sheet.worksheet_by_title(player)
        try:
            first_number_eff = player_sheet.get_value("O3")
            if first_number_eff is None or first_number_eff == "":
                raise Exception
        except:
            return self.get_player_effects(spread_sheet_id, player)

        try:
            eff = player_sheet.get_value(
                f"U{2 + (int(game_round) - int(first_number_eff) + 1)}"
            )
            return eff if eff is not None else ""
        except:
            return ""

    def get_player_mp(self, spread_sheet_id: str, player: str) -> int:
        players = self.get_players_name(spread_sheet_id)
        num = players.index(player)

        spread_sheet = self.table_session.open_by_key(spread_sheet_id)
        sheet = spread_sheet.worksheet_by_title("Основная")

        try:
            list_of_mp = list(np.array(sheet.get_values("G2", "G6")).ravel())
            if not list_of_mp:
                return self.get_player_mp(spread_sheet_id, player)
        except:
            return self.get_player_mp(spread_sheet_id, player)

        return list_of_mp[num]

    def get_game_spells(self, spread_sheet_id: str) -> dict:
        spread_sheet = self.table_session.open_by_key(spread_sheet_id)
        sheet = spread_sheet.worksheet_by_title("Описание")

        spells_info = sheet.get_values("A2", "G400")
        game_spells = {}

        for spell_info in spells_info:
            game_spells[spell_info[0].lower()] = (
                int(spell_info[6]) if int(spell_info[6]) != 0 else -100
            )

        return game_spells

    def create_astral_table(self, guild_id: int) -> None:
        spread_sheet = self.table_session.create(
            f"astral-{guild_id}", template=self.bot.database.get_tables()["astral"]
        )

        spread_sheet.share("", role="writer", type="anyone")
        sheet = spread_sheet.worksheet_by_title("Инфо")
        sheet.update_value("A2", f"{guild_id}")

        guild = self.bot.database.get_guild_info(guild_id)
        guild.astral_table = spread_sheet.id
        self.bot.database.session.commit()

    def create_temp_astral_table(
        self, uuid: str, template: Optional[str] = None
    ) -> pygsheets.Spreadsheet:
        spread_sheet: pygsheets.Spreadsheet = self.table_session.create(
            f"temp_astral-{uuid}",
            template=template
            if template is not None
            else self.bot.database.get_tables()["astral"],
        )

        spread_sheet.share("", role="writer", type="anyone")
        sheet = spread_sheet.worksheet_by_title("Инфо")
        sheet.update_value("B1", "=ScriptID()")
        sheet.update_value("B2", uuid)

        return spread_sheet

    def get_astral_script_id(self, sheet_url: str) -> str:
        spread_sheet: pygsheets.Spreadsheet = self.table_session.open_by_url(sheet_url)
        sheet = spread_sheet.worksheet_by_title("Инфо")

        return sheet.get_value("B1")

    # quiz

    def generate_quiz_table(self, uuid: str, questions_log: str):
        spread_sheet: pygsheets.Spreadsheet = self.table_session.create(title=uuid)
        spread_sheet.share("", type="anyone")

        sheet: pygsheets.Worksheet = spread_sheet.sheet1

        sheet.update_value("A1", "Блок")
        sheet.update_value("A2", "Вопрос")
        sheet.update_value("A3", "Ответ")

        sheet.update_value("A5", "Участники")
        for n, question in enumerate(questions_log):
            column_num = n + 2
            sheet.update_value((1, column_num), question["block"])
            sheet.update_value((2, column_num), question["text"])
            sheet.update_value((3, column_num), question["right_answer"])

            answers = question["answers"]
            members = []

            for member in answers:
                if member not in members:
                    sheet.update_value((6 + len(members), 1), member)
                    members.append(member)

                sheet.update_value(
                    (6 + members.index(member), column_num), answers[member]
                )

        return f"https://docs.google.com/spreadsheets/d/{spread_sheet.id}"
