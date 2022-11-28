from typing import Optional

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from modules.utils import make_async


class AstralSheetScriptApi:
    def __init__(self, script_id: Optional[str] = None):
        self.step: dict = {"function": "main"}
        self.end: dict = {"function": "endthisgame"}
        self.start: dict = {"function": "start"}

        SCOPES: list[str] = [
            "https://www.googleapis.com/auth/script.external_request",
            "https://www.googleapis.com/auth/script.container.ui",
            "https://www.googleapis.com/auth/script.container.ui",
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/script.deployments",
        ]

        creds = Credentials.from_authorized_user_file(
            r"./tokens/token_astral.json", SCOPES
        )

        self.api_service = build("script", "v1", credentials=creds)
        self.script_id: Optional[str] = script_id

    @make_async
    def start_game(self) -> dict:
        return (
            self.api_service.scripts()
            .run(body=self.start, scriptId=self.script_id)
            .execute()
        )

    @make_async
    def end_game(self) -> dict:
        return (
            self.api_service.scripts()
            .run(body=self.end, scriptId=self.script_id)
            .execute()
        )

    @make_async
    def next_round(self) -> dict:
        return (
            self.api_service.scripts()
            .run(body=self.step, scriptId=self.script_id)
            .execute()
        )

    @make_async
    def get_deployments(self, script_id):
        return (
            self.api_service.projects().deployments().list(scriptId=script_id).execute()
        )

    @make_async
    def deploy(self, script_id):
        return (
            self.api_service.projects()
            .deployments()
            .create(
                scriptId=script_id,
                body={  # Metadata the defines how a deployment is configured.
                    "description": "Auto Generated Deployment",  # The description for this deployment.
                    "manifestFileName": "appsscript",  # The manifest file name for this deployment.
                    "scriptId": script_id,  # The script project's Drive ID.
                    "versionNumber": -1,  # The version number on which this deployment is based.
                },
            )
            .execute()
        )
