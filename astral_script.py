from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from typing import Optional
import argparse


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

    def start_game(self) -> dict:
        return (
            self.api_service.scripts()
            .run(body=self.start, scriptId=self.script_id)
            .execute()
        )

    def end_game(self) -> dict:
        return (
            self.api_service.scripts()
            .run(body=self.end, scriptId=self.script_id)
            .execute()
        )

    def next_round(self) -> dict:
        return (
            self.api_service.scripts()
            .run(body=self.step, scriptId=self.script_id)
            .execute()
        )

    def get_deployments(self, script_id):
        return (
            self.api_service.projects().deployments().list(scriptId=script_id).execute()
        )

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--id", type=str, help="script id")
    parser.add_argument("-d", "--deploy", help="deploy script", action="store_true")
    parser.add_argument("-n", "--next", help="next round", action="store_true")
    parser.add_argument("-r", "--run", help="run game", action="store_true")
    parser.add_argument("-s", "--stop", help="stop game", action="store_true")
    args = parser.parse_args()

    if args.id is None:
        print("error: where is script id?")
        exit()

    API = AstralSheetScriptApi(args.id)

    input()

    try:
        if args.deploy:
            result = API.deploy(args.id)
        if args.next:
            result = API.next_round()
        if args.run:
            result = API.start_game()
        if args.stop:
            result = API.end_game()

        if "error" in result:
            print(f"error: {result}\n")
        else:
            if args.deploy:
                print(result["deploymentId"])
            else:
                print(result)

    except Exception as ex:
        print(f"error: {ex}\n")
