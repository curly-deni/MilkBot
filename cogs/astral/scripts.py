from googleapiclient.discovery import build
from oauth2client import file as oauth_file, client, tools


def connectToScriptsApi():
    SCOPES = [
        "https://www.googleapis.com/auth/script.external_request",
        "https://www.googleapis.com/auth/script.container.ui",
        "https://www.googleapis.com/auth/script.container.ui",
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/script.deployments"
    ]
    store = oauth_file.Storage("token_astral.json")
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets("token_astral.json", SCOPES)
        creds = tools.run_flow(flow, store)
    ApiService = build("script", "v1", credentials=creds)
    return ApiService


def startGame(ApiService, SCRIPT_ID):
    start = {"function": "start"}
    ApiService.scripts().run(body=start, scriptId=SCRIPT_ID).execute()


def endGame(ApiService, SCRIPT_ID):
    end = {"function": "endthisgame"}
    ApiService.scripts().run(body=end, scriptId=SCRIPT_ID).execute()


def nextRound(ApiService, SCRIPT_ID):
    change = {"function": "main"}
    ApiService.scripts().run(body=change, scriptId=SCRIPT_ID).execute()

def deploy(ApiService):
    ApiService.projects.deployments().create()

if __name__ == "__main__":
    service = connectToScriptsApi()
