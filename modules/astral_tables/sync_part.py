from typing import Optional

import pygsheets
from modules.utils import make_async
from nextcord.ext import tasks


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

    @make_async
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

    @make_async
    def delete_temp_astral_table(self, url: str):

        try:
            spread_sheet: pygsheets.Spreadsheet = self.table_session.open_by_url(url)
        except pygsheets.SpreadsheetNotFound:
            return

        try:
            spread_sheet.delete()
        except Exception as error:
            return error
