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

    def create_temp_astral_table(
        self, uuid: str, template: Optional[str] = None
    ) -> pygsheets.Spreadsheet:
        spread_sheet: pygsheets.Spreadsheet = self.table_session.create(
            f"temp_astral-{uuid}", template=template
        )

        spread_sheet.share("", role="writer", type="anyone")
        sheet = spread_sheet.worksheet_by_title("Инфо")
        sheet.update_value("B1", "=ScriptID()")
        sheet.update_value("B2", uuid)

        return spread_sheet
