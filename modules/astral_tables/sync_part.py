import pygsheets
from nextcord.ext import tasks
from typing import Optional


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
